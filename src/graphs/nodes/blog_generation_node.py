"""
博客生成节点 - 基于热点话题生成技术博客文章
支持多种大模型：Coze SDK、OpenAI、阿里百炼、DeepSeek、Kimi 等
"""
import os
import json
import logging
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import (
    BlogGenerationInput,
    BlogGenerationOutput,
    BlogContent,
    Article
)
from utils.llm_client import LLMClientFactory

logger = logging.getLogger(__name__)


def blog_generation_node(
    state: BlogGenerationInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> BlogGenerationOutput:
    """
    title: 博客生成
    desc: 基于选定的热点话题和相关文章，自动生成结构完整、专业的技术博客文章
    integrations: 大语言模型（支持 Coze SDK、OpenAI、阿里百炼、DeepSeek、Kimi 等）
    """
    # 读取LLM配置
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)

    llm_config_data = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    # 从selected_topic.related_articles标题列表匹配原始文章
    related_titles = state.selected_topic.related_articles
    matched_articles = []

    # 首先使用 selected_related_articles
    matched_articles = state.selected_related_articles.copy()

    # 如果不足，从raw_articles中补充匹配
    if len(matched_articles) < 3 and state.raw_articles:
        for raw_article in state.raw_articles:
            if raw_article not in matched_articles:
                # 检查标题是否相关
                for title in related_titles:
                    if title and raw_article.title and (
                        title.strip() in raw_article.title.strip() or
                        raw_article.title.strip() in title.strip()
                    ):
                        matched_articles.append(raw_article)
                        break

    # 如果仍然没有，使用所有原始文章的前几篇作为参考
    if not matched_articles and state.raw_articles:
        matched_articles = state.raw_articles[:5]

    # 构建相关文章参考
    references_text = []
    for idx, article in enumerate(matched_articles[:10], 1):
        references_text.append(f"- {article.title} ({article.source}): {article.url}")

    references_content = "\n".join(references_text)

    # 如果没有参考文章，使用话题描述作为内容基础
    if not references_content:
        references_content = f"暂无参考文章，基于以下话题描述生成：{state.selected_topic.description}"

    # 话题信息
    topic_info = f"话题: {state.selected_topic.topic}\n描述: {state.selected_topic.description}"

    # 渲染用户提示词
    up_tpl = Template(up)
    user_prompt = up_tpl.render({
        "topic_info": topic_info,
        "references": references_content
    })

    # 使用通用LLM客户端
    try:
        client = LLMClientFactory.from_config_file(cfg_file)
    except Exception as e:
        logger.error(f"初始化LLM客户端失败: {e}")
        # 回退到 Coze SDK
        from coze_coding_dev_sdk import LLMClient as CozeLLMClient
        from coze_coding_utils.runtime_ctx.context import new_context
        ctx = new_context(method="blog_generation")
        client = CozeLLMClient(ctx=ctx)

        messages = [
            SystemMessage(content=sp),
            HumanMessage(content=user_prompt)
        ]

        response = client.invoke(
            messages=messages,
            model=llm_config_data.get("model", "doubao-seed-2-0-pro-260215"),
            temperature=llm_config_data.get("temperature", 0.7),
            max_completion_tokens=llm_config_data.get("max_completion_tokens", 8000)
        )
    else:
        messages = [
            SystemMessage(content=sp),
            HumanMessage(content=user_prompt)
        ]
        response = client.invoke(messages=messages)

    # 解析响应内容
    content = response.content
    if isinstance(content, str):
        blog_text = content.strip()
    elif isinstance(content, list):
        blog_text = " ".join(str(item) for item in content)
    else:
        blog_text = str(content)

    # 提取标题和内容（假设LLM返回的是Markdown格式）
    lines = blog_text.split('\n')
    title = state.selected_topic.topic

    # 如果第一行是标题（以#开头），提取它
    for line in lines[:5]:
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # 构建参考链接列表
    reference_urls = [
        article.url for article in matched_articles[:10]
        if article.url
    ]

    # 构建博客内容对象
    blog_content = BlogContent(
        title=title,
        outline=[
            "引言",
            "话题概述",
            "技术细节",
            "实践应用",
            "总结与展望",
            "参考资料"
        ],
        content=blog_text,
        references=reference_urls
    )

    return BlogGenerationOutput(blog_content=blog_content)
