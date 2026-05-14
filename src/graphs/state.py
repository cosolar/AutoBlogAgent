"""
工作流全局状态定义
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class Article(BaseModel):
    """文章数据结构"""
    title: str = Field(..., description="文章标题")
    url: str = Field(..., description="文章URL")
    source: str = Field(..., description="文章来源平台")
    snippet: str = Field(default="", description="文章摘要/片段")
    publish_time: Optional[str] = Field(default=None, description="发布时间")
    author: Optional[str] = Field(default=None, description="作者")


class HotTopic(BaseModel):
    """热点话题结构"""
    topic: str = Field(..., description="话题名称")
    description: str = Field(..., description="话题描述")
    related_articles: List[str] = Field(default=[], description="相关文章标题列表")
    heat_score: float = Field(default=0.0, description="热度评分")


class BlogContent(BaseModel):
    """生成的博客内容结构"""
    title: str = Field(..., description="博客标题")
    outline: List[str] = Field(default=[], description="博客大纲")
    content: str = Field(default="", description="博客正文内容(Markdown格式)")
    references: List[str] = Field(default=[], description="参考文章链接")


class DailyTopic(BaseModel):
    """每日话题结构"""
    date: str = Field(..., description="日期")
    keywords: List[str] = Field(default=[], description="当日关键词")
    summary: str = Field(default="", description="当日摘要")


class GlobalState(BaseModel):
    """全局状态定义"""
    # 用户输入
    platforms: List[str] = Field(
        default=["github", "juejin", "csdn", "cnblogs"],
        description="要抓取的技术平台列表"
    )
    keywords: List[str] = Field(
        default=["开源", "AI", "编程", "技术趋势"],
        description="搜索关键词"
    )
    article_count_per_platform: int = Field(
        default=10,
        description="每个平台抓取的文章数量"
    )
    
    # RSS 订阅
    rss_url: str = Field(
        default="http://infinitum.shawnxie.top/api/daily/rss",
        description="RSS 订阅链接"
    )
    rss_topics: List[str] = Field(
        default=[],
        description="从 RSS 订阅提取的热门话题"
    )

    # 中间状态
    generated_topics: List[str] = Field(default=[], description="大模型生成的搜索话题")
    raw_articles: List[Article] = Field(default=[], description="抓取的原始文章列表")
    hot_topics: List[HotTopic] = Field(default=[], description="识别的热点话题列表")
    selected_topic: Optional[HotTopic] = Field(default=None, description="选中的热点话题")
    selected_related_articles: List[Article] = Field(default=[], description="选中话题相关的文章")
    blog_content: Optional[BlogContent] = Field(default=None, description="生成的博客内容")

    # 最终输出
    final_document_url: str = Field(default="", description="最终文档的URL")
    status_message: str = Field(default="", description="状态消息")


class GraphInput(BaseModel):
    """工作流输入"""
    platforms: List[str] = Field(
        default=["github", "juejin", "csdn", "cnblogs"],
        description="要抓取的技术平台列表"
    )
    keywords: List[str] = Field(
        default=["开源", "AI", "编程", "技术趋势"],
        description="搜索关键词"
    )
    article_count_per_platform: int = Field(
        default=10,
        description="每个平台抓取的文章数量"
    )
    rss_url: str = Field(
        default="http://infinitum.shawnxie.top/api/daily/rss",
        description="RSS 订阅链接（可选）"
    )


class GraphOutput(BaseModel):
    """工作流输出"""
    hot_topics: List[HotTopic] = Field(default=[], description="识别的热点话题列表")
    blog_content: Optional[BlogContent] = Field(default=None, description="生成的博客内容")
    document_url: str = Field(default="", description="最终文档URL")
    rss_topics: List[str] = Field(default=[], description="从RSS订阅提取的热门话题")
    daily_topics: List[DailyTopic] = Field(default=[], description="每日话题详情")


# ==================== 节点输入输出定义 ====================

class ArticleFetchInput(BaseModel):
    """文章抓取节点输入"""
    platforms: List[str] = Field(..., description="要抓取的技术平台列表")
    keywords: List[str] = Field(..., description="搜索关键词")
    article_count: int = Field(default=10, description="每个平台抓取数量")
    rss_topics: List[str] = Field(default=[], description="从RSS订阅提取的热门话题")


class ArticleFetchOutput(BaseModel):
    """文章抓取节点输出"""
    generated_topics: List[str] = Field(default=[], description="大模型生成的搜索话题")
    raw_articles: List[Article] = Field(default=[], description="抓取的文章列表")
    fetch_summary: str = Field(default="", description="抓取摘要")


class HotTopicAnalysisInput(BaseModel):
    """热点分析节点输入"""
    raw_articles: List[Article] = Field(..., description="待分析的文章列表")


class HotTopicAnalysisOutput(BaseModel):
    """热点分析节点输出"""
    hot_topics: List[HotTopic] = Field(default=[], description="识别的热点话题")


class TopicSelectionInput(BaseModel):
    """话题选择节点输入"""
    hot_topics: List[HotTopic] = Field(..., description="可选的热点话题列表")
    raw_articles: List[Article] = Field(default=[], description="原始文章列表")


class TopicSelectionOutput(BaseModel):
    """话题选择节点输出"""
    selected_topic: HotTopic = Field(..., description="选中的热点话题")
    selected_related_articles: List[Article] = Field(default=[], description="选中话题相关的文章列表")


class BlogGenerationInput(BaseModel):
    """博客生成节点输入"""
    selected_topic: HotTopic = Field(..., description="选中的热点话题")
    selected_related_articles: List[Article] = Field(default=[], description="选中话题相关的文章列表")
    raw_articles: List[Article] = Field(default=[], description="原始文章列表，用于补充参考")


class BlogGenerationOutput(BaseModel):
    """博客生成节点输出"""
    blog_content: BlogContent = Field(..., description="生成的博客内容")


class DocumentGenerationInput(BaseModel):
    """文档生成节点输入"""
    blog_content: BlogContent = Field(..., description="博客内容")


class DocumentGenerationOutput(BaseModel):
    """文档生成节点输出"""
    document_url: str = Field(..., description="生成的文档URL")


class RssSubscriptionInput(BaseModel):
    """RSS 订阅节点输入"""
    rss_url: str = Field(
        default="http://infinitum.shawnxie.top/api/daily/rss",
        description="RSS 订阅链接"
    )
    max_topics: int = Field(
        default=10,
        description="最多提取的话题数量"
    )


class RssSubscriptionOutput(BaseModel):
    """RSS 订阅节点输出"""
    rss_topics: List[str] = Field(default=[], description="从 RSS 提取的热门话题")
    daily_topics: List[DailyTopic] = Field(default=[], description="每日话题详情")
    rss_fetch_status: str = Field(default="", description="RSS 获取状态")
    status_message: str = Field(default="", description="状态消息")
