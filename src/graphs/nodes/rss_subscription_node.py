"""
RSS 订阅节点 - 从多个订阅源获取热门话题
支持 Infinitum AI 日报和 aihot.virxact.com
增强的错误处理和容错能力
"""

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import (
    ArticleFetchInput,
    ArticleFetchOutput,
    RssSubscriptionInput,
    RssSubscriptionOutput,
)


# 默认 RSS 订阅源列表
DEFAULT_RSS_SOURCES = [
    {
        "name": "Infinitum AI 日报",
        "url": "http://infinitum.shawnxie.top/api/daily/rss",
        "type": "daily_report"  # 日报格式，需要解析多天的内容
    },
    {
        "name": "AI Hot",
        "url": "https://aihot.virxact.com/feed/all.xml",
        "type": "feed"  # 普通 feed 格式
    }
]


def _fix_xml_content(xml_content: str) -> str:
    """
    修复可能损坏的 XML 内容
    处理 CDATA 未闭合、实体引用等问题
    """
    # 移除多余的 CDATA 包裹（可能造成问题）
    # 不做自动闭合，而是使用正则表达式提取内容

    # 移除控制字符
    xml_content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', xml_content)

    # 尝试修复未闭合的 CDATA
    open_cdata_count = xml_content.count('<![CDATA[')
    close_cdata_count = xml_content.count(']]>')

    if open_cdata_count != close_cdata_count:
        # 如果 CDATA 未闭合，尝试用正则提取 CDATA 内容
        cdata_contents = re.findall(r'<![CDATA[(.*?)(?:]]>|$)', xml_content, re.DOTALL)
        if cdata_contents:
            # 用临时标记替换未闭合的 CDATA
            for i, content in enumerate(cdata_contents):
                xml_content = xml_content.replace(
                    f'<![CDATA[{content}',
                    f'<![CDATA[{content}]]>',
                    1
                )

    # 确保 XML 根元素存在
    if not xml_content.strip().startswith('<'):
        # 尝试找到第一个 XML 标签开始的位置
        first_tag = xml_content.find('<')
        if first_tag > 0:
            xml_content = xml_content[first_tag:]

    return xml_content


def _extract_xml_content_regex(xml_content: str, tag_name: str) -> List[str]:
    """
    使用正则表达式提取 XML 标签内容（作为备用解析方法）
    """
    # 匹配 <tag>content</tag> 或 <tag><![CDATA[content]]></tag>
    pattern = rf'<{tag_name}>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</{tag_name}>'
    matches = re.findall(pattern, xml_content, re.DOTALL)
    return [m[0] or m[1] for m in matches if m[0] or m[1]]


def _extract_keywords_from_text(text: str) -> List[str]:
    """
    从文本中提取关键词/话题

    从 HTML 文本中提取被 <strong> 标签包裹的关键词，
    以及常见的 AI 相关术语作为话题
    """
    if not text:
        return []

    # 提取加粗的关键词
    bold_keywords = re.findall(r'<strong>([^<]+)</strong>', text)

    # 清理文本，移除 HTML 标签
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    # 合并提取的关键词
    all_keywords = list(set(bold_keywords))

    # 如果提取的关键词太少，尝试分割句子获取更多话题
    if len(all_keywords) < 5:
        sentences = clean_text.split('。')
        for sentence in sentences:
            if len(sentence) > 5 and len(sentence) < 50:
                # 提取名词短语作为话题
                topics = re.findall(r'([\u4e00-\u9fa5]{2,10}(?:AI|模型|技术|系统|平台|工具|框架|应用|服务))', sentence)
                all_keywords.extend(topics)

    # 去重并返回
    all_keywords = list(set(all_keywords))

    # 过滤掉太短或太长的关键词
    filtered_keywords = [k for k in all_keywords if 2 <= len(k) <= 20]

    return filtered_keywords


def _parse_rss_source(source: Dict, ctx: Context) -> tuple:
    """
    解析单个 RSS 源（增强错误处理）

    Returns:
        tuple: (keywords: List[str], daily_topics: List[Dict], status: str, error: Optional[str])
    """
    source_name = source["name"]
    source_url = source["url"]
    source_type = source["type"]

    try:
        from coze_coding_dev_sdk.fetch import FetchClient

        client = FetchClient(ctx=ctx)
        response = client.fetch(url=source_url)

        if response.status_code != 0:
            return ([], [], "failed", f"{source_name} fetch failed: {response.status_message}")

        # 解析 RSS 内容
        rss_xml = None
        for item in response.content:
            if item.type == "text":
                rss_xml = item.text
                break

        if not rss_xml:
            return ([], [], "failed", f"{source_name}: No RSS content found")

        keywords: List[str] = []
        daily_topics: List[Dict] = []

        # 尝试使用 ElementTree 解析
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(rss_xml)
        except ET.ParseError:
            # 如果标准 XML 解析失败，尝试修复内容后重试
            fixed_xml = _fix_xml_content(rss_xml)
            try:
                root = ET.fromstring(fixed_xml)
            except ET.ParseError:
                # 如果仍然失败，使用正则表达式提取
                root = None

        if root is not None:
            if source_type == "daily_report":
                # Infinitum AI 日报格式：解析多天日报
                items = root.findall('.//item')
                for item in items[:7]:  # 获取最近7天的日报
                    title = item.find('title')
                    desc = item.find('description')

                    if desc is not None and desc.text:
                        extracted = _extract_keywords_from_text(desc.text)
                        keywords.extend(extracted)

                        clean_desc = re.sub(r'<[^>]+>', '', desc.text)
                        clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()

                        daily_topics.append({
                            "source": source_name,
                            "date": title.text if title is not None else "Unknown",
                            "keywords": extracted[:5],
                            "summary": clean_desc[:200] + "..." if len(clean_desc) > 200 else clean_desc
                        })
            else:
                # 普通 feed 格式：解析标题和描述
                items = root.findall('.//item')
                for item in items[:15]:  # 获取最近15条
                    title = item.find('title')
                    desc = item.find('description')
                    link = item.find('link')

                    title_text = title.text if title is not None else ""
                    desc_text = desc.text if desc is not None else ""
                    link_text = link.text if link is not None else ""

                    # 从标题中提取关键词
                    if title_text:
                        # 清理标题
                        clean_title = re.sub(r'<[^>]+>', '', title_text)
                        # 提取关键词：通常是 2-10 个字符的中文或英文
                        title_keywords = re.findall(r'([\u4e00-\u9fa5]{2,15}|[a-zA-Z0-9\s]{3,30})', clean_title)
                        keywords.extend([k.strip() for k in title_keywords if len(k.strip()) >= 2])

                    # 从描述中提取关键词
                    if desc_text:
                        extracted = _extract_keywords_from_text(desc_text)
                        keywords.extend(extracted)

                        clean_desc = re.sub(r'<[^>]+>', '', desc_text)
                        clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()

                        if title_text:
                            daily_topics.append({
                                "source": source_name,
                                "title": clean_title[:100],
                                "keywords": extracted[:3],
                                "summary": clean_desc[:150] + "..." if len(clean_desc) > 150 else clean_desc,
                                "link": link_text[:200] if link_text else ""
                            })
        else:
            # 使用正则表达式作为备用解析方法
            if source_type == "daily_report":
                # 从 XML 中提取所有 item
                item_pattern = r'<item>(.*?)</item>'
                items = re.findall(item_pattern, rss_xml, re.DOTALL)[:7]

                for item_content in items:
                    titles = re.findall(r'<title>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</title>', item_content, re.DOTALL)
                    descs = re.findall(r'<description>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</description>', item_content, re.DOTALL)

                    title_text = titles[0][0] or titles[0][1] if titles else ""
                    desc_text = descs[0][0] or descs[0][1] if descs else ""

                    if desc_text:
                        extracted = _extract_keywords_from_text(desc_text)
                        keywords.extend(extracted)

                        clean_desc = re.sub(r'<[^>]+>', '', desc_text)
                        clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()

                        daily_topics.append({
                            "source": source_name,
                            "date": title_text or "Unknown",
                            "keywords": extracted[:5],
                            "summary": clean_desc[:200] + "..." if len(clean_desc) > 200 else clean_desc
                        })
            else:
                # 普通 feed 格式
                item_pattern = r'<item>(.*?)</item>'
                items = re.findall(item_pattern, rss_xml, re.DOTALL)[:15]

                for item_content in items:
                    titles = re.findall(r'<title>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</title>', item_content, re.DOTALL)
                    descs = re.findall(r'<description>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</description>', item_content, re.DOTALL)
                    links = re.findall(r'<link>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</link>', item_content, re.DOTALL)

                    title_text = titles[0][0] or titles[0][1] if titles else ""
                    desc_text = descs[0][0] or descs[0][1] if descs else ""
                    link_text = links[0][0] or links[0][1] if links else ""

                    if title_text:
                        clean_title = re.sub(r'<[^>]+>', '', title_text)
                        title_keywords = re.findall(r'([\u4e00-\u9fa5]{2,15}|[a-zA-Z0-9\s]{3,30})', clean_title)
                        keywords.extend([k.strip() for k in title_keywords if len(k.strip()) >= 2])

                    if desc_text:
                        extracted = _extract_keywords_from_text(desc_text)
                        keywords.extend(extracted)

                        clean_desc = re.sub(r'<[^>]+>', '', desc_text)
                        clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()

                        if title_text:
                            daily_topics.append({
                                "source": source_name,
                                "title": clean_title[:100],
                                "keywords": extracted[:3],
                                "summary": clean_desc[:150] + "..." if len(clean_desc) > 150 else clean_desc,
                                "link": link_text[:200] if link_text else ""
                            })

        return (keywords, daily_topics, "success", None)

    except Exception as e:
        return ([], [], "failed", f"{source_name}: {str(e)}")


def rss_subscription_node(
    state: RssSubscriptionInput,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> RssSubscriptionOutput:
    """
    title: RSS 订阅节点
    desc: 从多个 RSS 订阅源获取热门话题，自动提取关键词
    integrations: FetchClient
    """
    ctx = runtime.context

    # 获取 RSS 订阅源列表
    rss_urls = state.rss_urls if state.rss_urls else []

    # 构建订阅源列表
    sources = []
    for url in rss_urls:
        source_type = "feed"
        source_name = "RSS Feed"

        # 根据 URL 判断类型
        if "infinitum" in url.lower() or "daily" in url.lower():
            source_type = "daily_report"
            source_name = "Infinitum AI 日报"
        elif "aihot" in url.lower():
            source_type = "feed"
            source_name = "AI Hot"

        sources.append({
            "name": source_name,
            "url": url,
            "type": source_type
        })

    # 如果没有指定订阅源，使用默认列表
    if not sources:
        sources = DEFAULT_RSS_SOURCES

    # 并行获取所有订阅源
    all_keywords: List[str] = []
    all_daily_topics: List[Dict] = []
    errors: List[str] = []

    with ThreadPoolExecutor(max_workers=len(sources)) as executor:
        future_to_source = {
            executor.submit(_parse_rss_source, source, ctx): source
            for source in sources
        }

        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                keywords, daily_topics, status, error = future.result()

                if status == "success":
                    all_keywords.extend(keywords)
                    all_daily_topics.extend(daily_topics)
                else:
                    if error:
                        errors.append(error)

            except Exception as e:
                errors.append(f"{source['name']}: {str(e)}")

    # 统计关键词出现次数并排序
    from collections import Counter
    keyword_counts = Counter(all_keywords)

    # 获取前30个最常见的关键词
    top_keywords = [kw for kw, count in keyword_counts.most_common(30)]

    # 生成状态消息
    if top_keywords:
        status_message = f"成功从 {len(all_daily_topics)} 个话题中提取了 {len(top_keywords)} 个热门关键词"
        if errors:
            status_message += f"（{len(errors)} 个订阅源获取失败）"
    else:
        if errors:
            status_message = f"所有 RSS 源获取失败: {'; '.join(errors[:3])}"
        else:
            status_message = "未能从 RSS 源中提取到有效话题"

    # 将字典转换为 Article 对象
    from graphs.state import Article
    raw_articles = [
        Article(
            title=item.get('title', '未知标题'),
            url=item.get('link', item.get('url', '')),
            source=item.get('source', 'RSS'),
            snippet=item.get('description', ''),
            publish_time=item.get('pubDate'),
            author=item.get('author')
        )
        for item in all_daily_topics
    ]

    return ArticleFetchOutput(
        generated_topics=top_keywords,
        raw_articles=raw_articles,
        fetch_summary=status_message,
        status_message=status_message
    )
