"""
技术热点追踪与博客生成工作流主图
"""
from langgraph.graph import StateGraph, END
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig

from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput,
    ArticleFetchInput,
    ArticleFetchOutput,
    HotTopicAnalysisInput,
    HotTopicAnalysisOutput,
    TopicSelectionInput,
    TopicSelectionOutput,
    BlogGenerationInput,
    BlogGenerationOutput,
    DocumentGenerationInput,
    DocumentGenerationOutput,
    Article
)

# 导入节点函数
from graphs.nodes.article_fetch_node import article_fetch_node
from graphs.nodes.hot_topic_analysis_node import hot_topic_analysis_node
from graphs.nodes.topic_selection_node import topic_selection_node
from graphs.nodes.blog_generation_node import blog_generation_node
from graphs.nodes.document_generation_node import document_generation_node


# 创建状态图
builder = StateGraph(
    GlobalState,
    input_schema=GraphInput,
    output_schema=GraphOutput
)


def build_graph():
    """构建工作流图"""
    # 添加节点
    # 文章抓取节点 - 使用Web搜索技能
    builder.add_node(
        "article_fetch",
        article_fetch_node,
        metadata={"type": "task", "skill": "web-search"}
    )

    # 热点分析节点 - Agent节点
    builder.add_node(
        "hot_topic_analysis",
        hot_topic_analysis_node,
        metadata={"type": "agent", "llm_cfg": "config/hot_topic_analysis_llm_cfg.json"}
    )

    # 话题选择节点 - Task节点
    builder.add_node(
        "topic_selection",
        topic_selection_node,
        metadata={"type": "task"}
    )

    # 博客生成节点 - Agent节点
    builder.add_node(
        "blog_generation",
        blog_generation_node,
        metadata={"type": "agent", "llm_cfg": "config/blog_generation_llm_cfg.json"}
    )

    # 文档生成节点 - Task节点
    builder.add_node(
        "document_generation",
        document_generation_node,
        metadata={"type": "task", "skill": "document-generation"}
    )

    # 设置入口点
    builder.set_entry_point("article_fetch")

    # 添加边 - 线性流程
    builder.add_edge("article_fetch", "hot_topic_analysis")
    builder.add_edge("hot_topic_analysis", "topic_selection")
    builder.add_edge("topic_selection", "blog_generation")
    builder.add_edge("blog_generation", "document_generation")
    builder.add_edge("document_generation", END)

    # 编译图
    return builder.compile()


# 编译生成全局工作流
main_graph = build_graph()
