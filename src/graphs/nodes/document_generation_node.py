"""
文档生成节点 - 将博客内容生成为PDF文档
"""
import os
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import DocumentGenerationClient

from graphs.state import (
    DocumentGenerationInput,
    DocumentGenerationOutput,
    BlogContent
)


def document_generation_node(
    state: DocumentGenerationInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> DocumentGenerationOutput:
    """
    title: 文档生成
    desc: 将生成的博客内容转换为PDF文档格式
    integrations: 文档生成
    """
    # 构建Markdown格式的文档
    blog = state.blog_content

    markdown_content = f"""# {blog.title}

> 自动生成的技术博客 | 基于热点话题分析

---

## 引言

本文档基于当前技术热点话题自动生成，旨在为开发者提供最新、最实用的技术分析。

## 话题概述

**{blog.title}** 是当前技术领域的热门话题。

{blog.content}

## 总结与展望

本文档总结了当前技术热点的主要内容，希望能为读者提供有价值的参考。

---

## 参考资料

{chr(10).join(f"- [{ref}]({ref})" for ref in blog.references)}

---

*本文档由自动化工作流生成*
"""

    # 生成PDF文档
    client = DocumentGenerationClient()

    # 使用英文标题生成（用于文件名）
    import re
    safe_title = re.sub(r'[^a-zA-Z0-9]', '_', blog.title)[:50]

    try:
        document_url = client.create_pdf_from_markdown(
            markdown_content=markdown_content,
            title=f"tech_blog_{safe_title}"
        )
    except Exception as e:
        # 如果PDF生成失败，尝试生成DOCX
        document_url = client.create_docx_from_markdown(
            markdown_content=markdown_content,
            title=f"tech_blog_{safe_title}"
        )

    return DocumentGenerationOutput(document_url=document_url)
