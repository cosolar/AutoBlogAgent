"""
RSS 订阅节点 - 从多个订阅源获取热门话题
支持 Infinitum AI 日报和 aihot.virxact.com
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


def _extract_keywords_from_text(text: str) -> List[str]:
    """
    从文本中提取关键词/话题
    
    从 HTML 文本中提取被 <strong> 标签包裹的关键词，
    以及常见的 AI 相关术语作为话题
    """
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
    解析单个 RSS 源
    
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
        
        # 解析 XML
        import xml.etree.ElementTree as ET
        root = ET.fromstring(rss_xml)
        
        keywords: List[str] = []
        daily_topics: List[Dict] = []
        
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
        
        return (keywords, daily_topics, "success", None)
        
    except Exception as e:
        return ([], [], "failed", f"{source_name}: {str(e)}")


def rss_subscription_node(
    state: RssSubscriptionInput,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> RssSubscriptionOutput:
    """
    title: RSS 订阅话题提取
    desc: 从多个订阅源（Infinitum AI日报、AI Hot等）并行获取热门话题，提取关键词作为搜索话题
    integrations: fetch-url
    """
    ctx = runtime.context
    
    rss_urls = state.rss_urls
    max_topics = state.max_topics or 10
    
    # 构建 RSS 源列表
    rss_sources = []
    
    # 添加用户指定的 RSS 源
    if rss_urls:
        for url in rss_urls:
            if "infinitum" in url.lower():
                rss_sources.append({
                    "name": "Infinitum AI 日报",
                    "url": url,
                    "type": "daily_report"
                })
            else:
                rss_sources.append({
                    "name": "RSS Feed",
                    "url": url,
                    "type": "feed"
                })
    else:
        # 使用默认订阅源
        rss_sources = DEFAULT_RSS_SOURCES.copy()
    
    all_keywords: List[str] = []
    all_daily_topics: List[Dict] = []
    success_count = 0
    status_messages = []
    
    # 并行获取所有 RSS 源
    with ThreadPoolExecutor(max_workers=len(rss_sources)) as executor:
        future_to_source = {
            executor.submit(_parse_rss_source, source, ctx): source
            for source in rss_sources
        }
        
        for future in as_completed(future_to_source):
            keywords, daily_topics, status, error = future.result()
            
            if status == "success":
                all_keywords.extend(keywords)
                all_daily_topics.extend(daily_topics)
                success_count += 1
            else:
                status_messages.append(error)
    
    # 去重
    all_keywords = list(set(all_keywords))
    
    # 按出现次数排序（模拟热度）
    keyword_counts: Dict[str, int] = {}
    for keyword in all_keywords:
        keyword_counts[keyword] = all_keywords.count(keyword)
    
    # 选择最热门的话题
    hot_topics = sorted(keyword_counts.keys(), key=lambda x: keyword_counts[x], reverse=True)[:max_topics]
    
    if success_count > 0:
        status_message = f"成功从 {success_count}/{len(rss_sources)} 个 RSS 源获取 {len(hot_topics)} 个热门话题"
        if status_messages:
            status_message += f"（{len(status_messages)} 个源失败）"
        return RssSubscriptionOutput(
            rss_topics=hot_topics,
            daily_topics=all_daily_topics,
            rss_fetch_status="success",
            status_message=status_message
        )
    else:
        return RssSubscriptionOutput(
            rss_topics=[],
            daily_topics=[],
            rss_fetch_status="failed",
            status_message=f"所有 RSS 源获取失败: {'; '.join(status_messages)}"
        )
