"""
节点模块
"""
from graphs.nodes.article_fetch_node import article_fetch_node
from graphs.nodes.hot_topic_analysis_node import hot_topic_analysis_node
from graphs.nodes.topic_selection_node import topic_selection_node
from graphs.nodes.blog_generation_node import blog_generation_node
from graphs.nodes.document_generation_node import document_generation_node

__all__ = [
    "article_fetch_node",
    "hot_topic_analysis_node",
    "topic_selection_node",
    "blog_generation_node",
    "document_generation_node"
]
