"""
RSS 订阅节点 - 从 Infinitum AI 日报订阅源获取热门话题
"""

import json
import os
import re
from typing import List, Dict

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import (
    ArticleFetchInput,
    ArticleFetchOutput,
    RssSubscriptionInput,
    RssSubscriptionOutput,
)


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


def rss_subscription_node(
    state: RssSubscriptionInput,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> RssSubscriptionOutput:
    """
    title: RSS 订阅话题提取
    desc: 从 Infinitum AI 日报订阅源获取热门话题，提取关键词作为搜索话题
    integrations: fetch-url
    """
    ctx = runtime.context
    
    rss_url = state.rss_url
    max_topics = state.max_topics or 10
    
    try:
        # 使用 fetch-url 技能获取 RSS 内容
        from coze_coding_dev_sdk.fetch import FetchClient
        
        client = FetchClient(ctx=ctx)
        response = client.fetch(url=rss_url)
        
        if response.status_code != 0:
            raise Exception(f"Failed to fetch RSS: {response.status_message}")
        
        # 解析 XML 格式的内容
        # RSS 内容在 text 字段中
        rss_xml = None
        for item in response.content:
            if item.type == "text":
                rss_xml = item.text
                break
        
        if not rss_xml:
            raise Exception("No RSS content found in response")
        
        # 解析 XML
        import xml.etree.ElementTree as ET
        root = ET.fromstring(rss_xml)
        
        # 提取所有 item 的描述
        items = root.findall('.//item')
        
        all_keywords: List[str] = []
        daily_topics: List[Dict[str, str]] = []
        
        for item in items[:7]:  # 获取最近7天的日报
            title = item.find('title')
            desc = item.find('description')
            
            if desc is not None and desc.text:
                keywords = _extract_keywords_from_text(desc.text)
                all_keywords.extend(keywords)
                
                # 清理描述用于记录
                clean_desc = re.sub(r'<[^>]+>', '', desc.text)
                clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
                
                daily_topics.append({
                    "date": title.text if title is not None else "Unknown",
                    "keywords": keywords[:5],  # 每日报保留前5个关键词
                    "summary": clean_desc[:200] + "..." if len(clean_desc) > 200 else clean_desc
                })
        
        # 去重
        all_keywords = list(set(all_keywords))
        
        # 按出现次数排序（模拟热度）
        keyword_counts: Dict[str, int] = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = all_keywords.count(keyword)
        
        # 选择最热门的话题
        hot_topics = sorted(keyword_counts.keys(), key=lambda x: keyword_counts[x], reverse=True)[:max_topics]
        
        return RssSubscriptionOutput(
            rss_topics=hot_topics,
            daily_topics=daily_topics,
            rss_fetch_status="success",
            status_message=f"成功从 RSS 获取 {len(hot_topics)} 个热门话题"
        )
        
    except Exception as e:
        # 如果 RSS 获取失败，返回空话题列表
        return RssSubscriptionOutput(
            rss_topics=[],
            daily_topics=[],
            rss_fetch_status="failed",
            status_message=f"RSS 获取失败: {str(e)}"
        )
