"""
文章抓取节点 - 调用大模型生成话题 + 并行搜索多平台热门文章
"""
import os
import json
import re
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context

from utils.llm_client import LLMClientFactory

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
    desc: 合并RSS话题和大模型生成话题，并行从多平台抓取热门文章数据
    integrations: 大语言模型, Web搜索
    """
    ctx = new_context(method="article_fetch")

    # ========== 步骤1: 获取话题来源 ==========
    # 优先使用 RSS 订阅的话题
    rss_topics = state.rss_topics if hasattr(state, 'rss_topics') else []
    
    if rss_topics:
        # 如果有 RSS 话题，直接使用
        generated_topics = rss_topics
        topic_source = "RSS订阅"
    else:
        # 否则调用大模型生成话题
        generated_topics = _generate_topics(state.keywords, config, ctx)
        topic_source = "大模型生成"

    # ========== 步骤2: 并行搜索所有话题 ==========
    articles = _parallel_search(
        topics=generated_topics,
        platforms=state.platforms,
        article_count=state.article_count,
        ctx=ctx
    )

    # ========== 步骤3: 汇总结果 ==========
    summary = f"话题来源: {topic_source}，共 {len(generated_topics)} 个话题，从 {len(set(a.source for a in articles))} 个平台抓取到 {len(articles)} 篇相关文章"

    return ArticleFetchOutput(
        generated_topics=generated_topics,
        raw_articles=articles,
        fetch_summary=summary
    )


def _generate_topics(keywords: List[str], config: RunnableConfig, ctx: Context) -> List[str]:
    """
    调用大模型生成热门AI话题
    """
    # 获取LLM配置
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH", ""), config['metadata'].get('topic_llm_cfg', 'config/topic_generation_llm_cfg.json'))

    # 读取配置文件获取提示词
    with open(cfg_file, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # 创建LLM客户端
    llm = LLMClientFactory.from_config_file(cfg_file)

    # 渲染提示词
    keywords_str = "、".join(keywords) if keywords else "AI技术"
    user_prompt = cfg.get('up', '').replace('{{ keywords }}', keywords_str)

    # 构建消息列表
    from langchain_core.messages import SystemMessage, HumanMessage
    sp = cfg.get('sp', '你是一个专业的AI技术话题分析师。')
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt)
    ]

    # 调用大模型
    response = llm.invoke(messages=messages)

    # 解析响应内容
    content = response.content
    if isinstance(content, str):
        response_text = content.strip()
    elif isinstance(content, list):
        response_text = " ".join(str(item) for item in content)
    else:
        response_text = str(content)

    # 解析话题列表
    topics = []
    for line in response_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        # 解析格式: 话题名称|描述 或 直接是话题名称
        if '|' in line:
            topic_name = line.split('|')[0].strip()
        else:
            topic_name = line.strip().lstrip('0123456789.-、）) ')

        if topic_name and len(topic_name) <= 50:
            topics.append(topic_name)

    # 确保至少有默认话题
    if not topics:
        topics = [
            "AI编程工具 Cursor 使用指南",
            "大模型应用开发 LangChain实战",
            "开源AI项目 GitHub热门推荐",
            "机器学习框架 PyTorch vs TensorFlow",
            "AI技术趋势 2024最火方向"
        ]

    return topics[:12]  # 最多12个话题


def _parallel_search(
    topics: List[str],
    platforms: List[str],
    article_count: int,
    ctx: Context
) -> List[Article]:
    """
    并行搜索所有话题和平台
    """
    # 平台域名映射
    platform_domains = {
        "github": "github.com",
        "juejin": "juejin.cn",
        "csdn": "csdn.net",
        "cnblogs": "cnblogs.com"
    }

    # 获取需要搜索的平台
    search_platforms = {
        p: domain for p, domain in platform_domains.items()
        if p in platforms
    }

    if not search_platforms:
        # 如果没有指定平台，使用所有平台
        search_platforms = platform_domains

    # 构建搜索任务列表
    search_tasks: List[Tuple[str, str, str]] = []  # (话题, 平台名, 域名)
    for topic in topics:
        for platform_name, domain in search_platforms.items():
            search_tasks.append((topic, platform_name, domain))

    # 并行执行搜索
    all_articles: List[Article] = []

    def search_single(task: Tuple[str, str, str]) -> List[Article]:
        topic, platform_name, domain = task
        articles = []
        try:
            search_client = SearchClient(ctx=ctx)
            response = search_client.search(
                query=topic,
                search_type="web",
                count=article_count,
                sites=domain,
                need_summary=True,
                time_range="1m"  # 最近一个月
            )

            for item in response.web_items:
                article = Article(
                    title=item.title or "",
                    url=item.url or "",
                    source=platform_name,
                    snippet=item.snippet or item.summary or "",
                    publish_time=item.publish_time,
                    author=None
                )
                articles.append(article)
        except Exception as e:
            pass
        return articles

    # 使用线程池并行搜索
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(search_single, task) for task in search_tasks]
        for future in as_completed(futures):
            try:
                articles = future.result()
                all_articles.extend(articles)
            except Exception:
                continue

    # 去重（基于URL）
    unique_articles = []
    seen_urls = set()
    for article in all_articles:
        if article.url and article.url not in seen_urls:
            seen_urls.add(article.url)
            unique_articles.append(article)

    return unique_articles
