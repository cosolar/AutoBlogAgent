"""
文章抓取节点 - 从多个技术平台抓取热门文章
"""
import os
import json
from typing import List
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context

from graphs.state import (
    ArticleFetchInput,
    ArticleFetchOutput,
    Article
)


def article_fetch_node(
    state: ArticleFetchInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ArticleFetchOutput:
    """
    title: 文章抓取
    desc: 从GitHub、掘金、CSDN、博客园等指定技术平台自动抓取热门文章数据
    integrations: Web搜索
    """
    ctx = new_context(method="article_fetch")

    # 平台域名映射
    platform_domains = {
        "github": "github.com",
        "juejin": "juejin.cn",
        "csdn": "csdn.net",
        "cnblogs": "cnblogs.com"
    }

    all_articles: List[Article] = []
    search_client = SearchClient(ctx=ctx)

    # 获取已启用的平台
    enabled_platforms = [
        (p, domain)
        for p, domain in platform_domains.items()
        if p in state.platforms
    ]

    # 对每个关键词进行搜索
    for keyword in state.keywords:
        for platform_name, domain in enabled_platforms:
            try:
                # 使用Web搜索API搜索指定站点的文章
                response = search_client.search(
                    query=keyword,
                    search_type="web",
                    count=state.article_count,
                    sites=domain,
                    need_summary=True,
                    time_range="1m"  # 最近一个月
                )

                # 解析搜索结果
                for item in response.web_items:
                    article = Article(
                        title=item.title or "",
                        url=item.url or "",
                        source=platform_name,
                        snippet=item.snippet or item.summary or "",
                        publish_time=item.publish_time,
                        author=None
                    )
                    all_articles.append(article)

            except Exception as e:
                # 记录错误但不中断流程
                continue

    # 去重（基于URL）
    unique_articles = []
    seen_urls = set()
    for article in all_articles:
        if article.url and article.url not in seen_urls:
            seen_urls.add(article.url)
            unique_articles.append(article)

    # 生成摘要
    summary = f"从 {len(set(state.platforms) & set(platform_domains.keys()))} 个平台抓取到 {len(unique_articles)} 篇相关文章"

    return ArticleFetchOutput(
        raw_articles=unique_articles,
        fetch_summary=summary
    )
