"""
话题选择节点 - 从多个热点话题中选择最适合写博客的话题
"""
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import (
    TopicSelectionInput,
    TopicSelectionOutput,
    HotTopic,
    Article
)


def topic_selection_node(
    state: TopicSelectionInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> TopicSelectionOutput:
    """
    title: 话题选择
    desc: 从识别出的热点话题中选择最热门或最适合的主题，并匹配相关文章
    integrations: 无
    """
    # 选择热度最高的话题
    if not state.hot_topics:
        # 防御性处理
        return TopicSelectionOutput(
            selected_topic=HotTopic(
                topic="默认技术话题",
                description="一个有趣的技术话题",
                heat_score=5.0
            ),
            selected_related_articles=[]
        )

    # 按热度排序，选择最高的话题
    sorted_topics = sorted(state.hot_topics, key=lambda x: x.heat_score, reverse=True)
    selected = sorted_topics[0]

    # 根据selected.related_articles中的标题匹配原始文章
    related_titles = selected.related_articles
    matched_articles = []

    for raw_article in state.raw_articles:
        for title in related_titles:
            if title and raw_article.title and title.strip() == raw_article.title.strip():
                matched_articles.append(raw_article)
                break

    # 如果没有匹配到文章，使用原始文章的前几篇
    if not matched_articles:
        matched_articles = state.raw_articles[:5]

    return TopicSelectionOutput(
        selected_topic=selected,
        selected_related_articles=matched_articles
    )
