"""
文章抓取节点
使用话题直接搜索并抓取相关文章
"""
import os
import json
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from jinja2 import Template

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import (
    ArticleFetchInput,
    ArticleFetchOutput,
    Article,
    GlobalState
)

logger = logging.getLogger(__name__)


def _search_articles(topic: str, count: int, config: RunnableConfig, ctx: Context) -> List[Article]:
    """使用话题搜索相关文章"""
    articles = []
    
    try:
        from coze_coding_dev_sdk import SearchClient
        
        # 使用 SearchClient 进行搜索
        client = SearchClient(ctx=ctx)
        
        # 构造搜索查询 - 使用话题作为关键词
        query = f"{topic} 技术 教程"
        
        # 调用搜索
        response = client.web_search(query=query, count=count)
        
        if response and hasattr(response, 'web_items') and response.web_items:
            for item in response.web_items:
                url = item.url if hasattr(item, 'url') else ""
                article = Article(
                    title=item.title if hasattr(item, 'title') else "",
                    url=url,
                    source=_extract_source(url),
                    snippet=item.content if hasattr(item, 'content') else "",
                    publish_time=getattr(item, 'publish_time', None),
                    author=getattr(item, 'author', None)
                )
                if article.title and article.url:
                    articles.append(article)
        
        logger.info(f"话题 '{topic}' 搜索到 {len(articles)} 篇文章")
        
    except Exception as e:
        logger.warning(f"搜索话题 '{topic}' 失败: {str(e)}")
    
    return articles


def _extract_source(url: str) -> str:
    """从URL提取来源平台"""
    if not url:
        return "unknown"
    
    if "github.com" in url:
        return "github"
    elif "juejin.cn" in url:
        return "掘金"
    elif "csdn.net" in url:
        return "CSDN"
    elif "cnblogs.com" in url:
        return "博客园"
    elif "zhihu.com" in url:
        return "知乎"
    elif "bilibili.com" in url:
        return "B站"
    elif "baidu.com" in url:
        return "百度"
    else:
        return "other"


def article_fetch_node(
    state: ArticleFetchInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ArticleFetchOutput:
    """
    title: 文章抓取
    desc: 基于热门话题搜索并抓取相关文章，使用百度搜索
    integrations: Web搜索
    """
    ctx = runtime.context
    
    # 获取话题列表 - 优先使用 RSS 话题
    topics = state.rss_topics if state.rss_topics else []
    
    # 如果没有话题，返回空
    if not topics:
        logger.warning("没有可用的话题，返回空文章列表")
        return ArticleFetchOutput(
            generated_topics=[],
            raw_articles=[],
            fetch_summary="没有可用的话题"
        )
    
    all_articles: List[Article] = []
    articles_per_topic = max(1, state.article_count // len(topics)) if topics else 1
    
    logger.info(f"开始基于 {len(topics)} 个话题搜索文章，每个话题 {articles_per_topic} 篇")
    
    # 并行搜索每个话题
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_topic = {
            executor.submit(_search_articles, topic, articles_per_topic, config, ctx): topic
            for topic in topics
        }
        
        for future in as_completed(future_to_topic):
            topic = future_to_topic[future]
            try:
                articles = future.result()
                all_articles.extend(articles)
                logger.info(f"话题 '{topic}' 完成，获取 {len(articles)} 篇文章")
            except Exception as e:
                logger.error(f"处理话题 '{topic}' 时出错: {str(e)}")
    
    # 去重
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article.url and article.url not in seen_urls:
            seen_urls.add(article.url)
            unique_articles.append(article)
    
    logger.info(f"去重后共获取 {len(unique_articles)} 篇独特文章")
    
    # 构建摘要
    sources_count = {}
    for article in unique_articles:
        sources_count[article.source] = sources_count.get(article.source, 0) + 1
    
    summary_parts = [f"共抓取 {len(unique_articles)} 篇文章"]
    if sources_count:
        source_info = ", ".join([f"{k}:{v}篇" for k, v in sorted(sources_count.items(), key=lambda x: -x[1])])
        summary_parts.append(f"来源分布: {source_info}")
    
    return ArticleFetchOutput(
        generated_topics=topics,
        raw_articles=unique_articles,
        fetch_summary="; ".join(summary_parts)
    )
