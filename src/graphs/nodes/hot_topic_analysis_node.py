"""
热点话题识别节点 - 使用LLM分析文章并识别热点话题
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
    HotTopicAnalysisInput,
    HotTopicAnalysisOutput,
    Article,
    HotTopic
)
from utils.llm_client import LLMClientFactory

logger = logging.getLogger(__name__)


def hot_topic_analysis_node(
    state: HotTopicAnalysisInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> HotTopicAnalysisOutput:
    """
    title: 热点话题识别
    desc: 使用大语言模型从抓取的文章中分析并识别时下技术热点话题
    integrations: 大语言模型（支持 Coze SDK、OpenAI、阿里百炼、DeepSeek、Kimi 等）
    """
    # 读取LLM配置
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)

    llm_config_data = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    # 构建文章摘要文本
    articles_text = []
    for idx, article in enumerate(state.raw_articles[:30], 1):  # 最多分析30篇
        articles_text.append(f"{idx}. 【{article.source}】{article.title}\n   摘要: {article.snippet[:200]}...")

    articles_content = "\n\n".join(articles_text)

    # 渲染用户提示词
    up_tpl = Template(up)
    user_prompt = up_tpl.render({"articles": articles_content})

    # 使用通用LLM客户端
    try:
        client = LLMClientFactory.from_config_file(cfg_file)
    except Exception as e:
        logger.error(f"初始化LLM客户端失败: {e}")
        # 回退到 Coze SDK
        from coze_coding_dev_sdk import LLMClient as CozeLLMClient
        from coze_coding_utils.runtime_ctx.context import new_context
        ctx = new_context(method="hot_topic_analysis")
        client = CozeLLMClient(ctx=ctx)

        messages = [
            SystemMessage(content=sp),
            HumanMessage(content=user_prompt)
        ]

        response = client.invoke(
            messages=messages,
            model=llm_config_data.get("model", "doubao-seed-2-0-lite-260215"),
            temperature=llm_config_data.get("temperature", 0.7),
            max_completion_tokens=llm_config_data.get("max_completion_tokens", 4000)
        )
    else:
        messages = [
            SystemMessage(content=sp),
            HumanMessage(content=user_prompt)
        ]
        response = client.invoke(messages=messages)

    # 解析LLM返回的热点话题
    content = response.content
    if isinstance(content, str):
        response_text = content.strip()
    elif isinstance(content, list):
        response_text = " ".join(str(item) for item in content)
    else:
        response_text = str(content)

    # 尝试解析JSON格式的响应
    hot_topics = []
    try:
        # 尝试从响应中提取JSON
        import re
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            topics_data = json.loads(json_match.group())
            for topic_data in topics_data:
                hot_topic = HotTopic(
                    topic=topic_data.get("topic", ""),
                    description=topic_data.get("description", ""),
                    related_articles=topic_data.get("related_articles", []),
                    heat_score=topic_data.get("heat_score", 0.0)
                )
                hot_topics.append(hot_topic)
    except Exception:
        # 如果解析失败，手动构建
        pass

    # 如果没有解析到有效话题，创建一个默认话题
    if not hot_topics:
        hot_topics.append(HotTopic(
            topic="技术热点综合分析",
            description="基于多个平台热门文章的综合分析",
            related_articles=[a.title for a in state.raw_articles[:5]],
            heat_score=8.5
        ))

    return HotTopicAnalysisOutput(hot_topics=hot_topics)
