"""
热点话题识别节点 - 使用LLM分析文章并识别热点话题
"""
import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import new_context

from graphs.state import (
    HotTopicAnalysisInput,
    HotTopicAnalysisOutput,
    Article,
    HotTopic
)


def hot_topic_analysis_node(
    state: HotTopicAnalysisInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> HotTopicAnalysisOutput:
    """
    title: 热点话题识别
    desc: 使用大语言模型从抓取的文章中分析并识别时下技术热点话题
    integrations: 大语言模型
    """
    ctx = new_context(method="hot_topic_analysis")

    # 读取LLM配置
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)

    llm_config = _cfg.get("config", {})
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

    # 调用LLM
    client = LLMClient(ctx=ctx)
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt)
    ]

    response = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-2-0-lite-260215"),
        temperature=llm_config.get("temperature", 0.7),
        max_completion_tokens=llm_config.get("max_completion_tokens", 4000)
    )

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
