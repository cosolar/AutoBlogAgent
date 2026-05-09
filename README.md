# 🚀 Tech Blog Generator - 智能技术博客生成器

> 自动追踪 GitHub、掘金、CSDN、博客园等技术平台的热点文章，智能识别热点话题，生成专业完整的技术博客文档

[English](README_EN.md) | 中文

---

## 📖 项目简介

**Tech Blog Generator** 是一款基于 AI 的自动化技术博客生成工具。它能够自动从多个主流技术平台抓取热门文章，利用大语言模型分析识别当前最热门的技术话题，并自动生成结构完整、内容专业的技术博客文章，最终导出为可下载的 PDF 文档。

### 核心特性

- 🔍 **多平台文章抓取** - 支持 GitHub、掘金、CSDN、博客园等主流技术平台
- 🧠 **AI 热点识别** - 使用大语言模型智能分析，识别技术热点话题
- ✍️ **自动博客生成** - 生成结构清晰、内容专业的技术博客文章
- 📄 **PDF 文档导出** - 一键生成可分享的 PDF 文档
- ⚙️ **高度可定制** - 支持自定义搜索关键词、平台选择、文章数量等参数

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Tech Blog Generator 工作流                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   文章抓取    │───▶│   热点分析    │───▶│   话题选择    │      │
│  │ article_     │    │ hot_topic_   │    │ topic_       │      │
│  │    fetch     │    │  analysis    │    │  selection   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                  │               │
│                                                  ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   文档生成    │◀───│   博客生成    │◀───│   博客生成    │      │
│  │ document_    │    │ blog_        │    │ blog_        │      │
│  │  generation  │    │ generation   │    │ generation   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 工作流节点说明

| 节点名称 | 类型 | 功能描述 |
|---------|------|---------|
| `article_fetch` | Task | 从指定技术平台抓取热门文章数据 |
| `hot_topic_analysis` | Agent | 使用 LLM 分析文章，识别热点话题 |
| `topic_selection` | Task | 从多个热点中选择最热门的话题 |
| `blog_generation` | Agent | 基于热点话题生成完整的技术博客 |
| `document_generation` | Task | 将博客转换为 PDF 文档 |

---

## 🎯 功能详解

### 1. 多平台文章抓取

支持从以下技术平台自动抓取热门文章：

| 平台 | 域名 | 说明 |
|------|------|------|
| GitHub | github.com | 热门开源项目和开发讨论 |
| 掘金 | juejin.cn | 国内领先的技术社区 |
| CSDN | csdn.net | 老牌程序员技术社区 |
| 博客园 | cnblogs.com | 资深开发者博客平台 |

**抓取策略：**
- 支持多关键词并行搜索
- 自动去重，保证文章唯一性
- 智能提取文章标题、摘要、发布时间等信息

### 2. AI 热点话题识别

使用大语言模型对抓取的文章进行深度分析：

```
输入：20-30 篇技术文章
      ↓
AI 分析：
  - 提取关键技术主题词
  - 统计主题出现频次
  - 评估话题热度评分
      ↓
输出：3-5 个热点话题列表
      每个话题包含：
      - 话题名称
      - 话题描述
      - 相关文章列表
      - 热度评分 (0-10)
```

### 3. 智能话题选择

- 自动选择热度最高的话题
- 支持按话题生成对应的技术博客
- 保留所有识别的热点话题供参考

### 4. 专业博客生成

生成的技术博客包含完整的文章结构：

```markdown
# 文章标题

> 自动生成的技术博客 | 基于热点话题分析

---

## 引言
## 话题概述
## 技术细节/核心原理
## 实践应用/案例分析
## 总结与展望
## 参考资料
```

**博客特点：**
- 中文写作，符合国内开发者阅读习惯
- 结构清晰，逻辑严谨
- 内容专业但不晦涩
- 字数通常在 1500 字以上
- 包含完整的参考资料链接

### 5. PDF 文档导出

- 自动将博客转换为专业 PDF 文档
- 支持中文字体
- 自动生成目录结构
- 可直接下载和分享

---

## 🛠️ 技术栈

### 核心技术

- **工作流编排**: LangGraph
- **大语言模型**: Doubao Seed / DeepSeek / Kimi
- **文章搜索**: Web Search API
- **文档生成**: PDF Generation API

### 开发框架

```
Python >= 3.10
├── langgraph          # 工作流编排框架
├── langchain-core     # 消息传递和工具定义
├── coze-coding-dev-sdk # 集成 SDK
└── pydantic           # 数据验证
```

### 项目结构

```
├── src/
│   ├── graphs/                    # 工作流核心代码
│   │   ├── state.py              # 全局状态定义
│   │   ├── graph.py              # 主图编排
│   │   └── nodes/                # 节点实现
│   │       ├── article_fetch_node.py
│   │       ├── hot_topic_analysis_node.py
│   │       ├── topic_selection_node.py
│   │       ├── blog_generation_node.py
│   │       └── document_generation_node.py
│   └── main.py                   # 程序入口
├── config/                       # 配置文件
│   ├── hot_topic_analysis_llm_cfg.json
│   └── blog_generation_llm_cfg.json
├── tests/                        # 测试用例
├── AGENTS.md                     # 项目规范文档
└── README.md                     # 项目说明文档
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 网络连接（用于访问搜索 API）

### 安装依赖

```bash
# 使用 uv 安装依赖（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 基本使用

```python
from src.graphs.graph import main_graph

# 定义工作流输入
input_data = {
    "platforms": ["github", "juejin", "csdn", "cnblogs"],  # 要抓取的平台
    "keywords": ["开源", "AI", "编程", "技术趋势"],         # 搜索关键词
    "article_count_per_platform": 10                        # 每个平台的文章数量
}

# 执行工作流
result = main_graph.invoke(input_data)

# 获取结果
print("识别的热点话题:", result["hot_topics"])
print("生成的博客:", result["blog_content"]["title"])
print("文档下载链接:", result["document_url"])
```

### 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:------:|:----:|:----:|:------:|:-----|
| `platforms` | List[str] | 否 | `["github", "juejin", "csdn", "cnblogs"]` | 要抓取的技术平台 |
| `keywords` | List[str] | 否 | `["开源", "AI", "编程", "技术趋势"]` | 搜索关键词列表 |
| `article_count_per_platform` | int | 否 | `10` | 每个平台抓取的文章数量 |

### 输出结构

```python
{
    "hot_topics": [
        {
            "topic": "AI编程工具与实践",
            "description": "介绍AI编程技术发展...",
            "related_articles": ["文章1", "文章2", ...],
            "heat_score": 9.5
        },
        ...
    ],
    "blog_content": {
        "title": "文章标题",
        "outline": ["引言", "话题概述", ...],
        "content": "# Markdown 格式的文章内容",
        "references": ["url1", "url2", ...]
    },
    "document_url": "https://xxx.pdf"
}
```

---

## 💡 使用场景

### 1. 技术博主

快速获取最新技术热点，生成博客草稿，提高创作效率。

### 2. 技术团队

定期生成技术趋势报告，帮助团队了解行业动态。

### 3. 内容运营

自动化生成技术内容，支持公众号、技术社区等内容分发。

### 4. 个人学习

追踪感兴趣的技术领域，生成学习笔记和总结。

---

## 🔧 高级配置

### 自定义 LLM 配置

编辑 `config/` 目录下的 JSON 配置文件：

```json
{
    "config": {
        "model": "doubao-seed-2-0-pro-260215",
        "temperature": 0.7,
        "max_completion_tokens": 8000
    },
    "sp": "你的系统提示词...",
    "up": "你的用户提示词..."
}
```

### 支持的模型

| 模型 ID | 说明 |
|---------|------|
| `doubao-seed-2-0-pro-260215` | 旗舰级全能模型，适合复杂任务 |
| `doubao-seed-2-0-lite-260215` | 均衡型模型，性价比高 |
| `deepseek-v3-2-251201` | DeepSeek V3.2 模型 |
| `kimi-k2-5-260127` | Kimi K2.5 模型 |

### 自定义搜索平台

在 `article_fetch_node.py` 中修改 `platform_domains`：

```python
platform_domains = {
    "github": "github.com",
    "juejin": "juejin.cn",
    "csdn": "csdn.net",
    "cnblogs": "cnblogs.com",
    # 添加自定义平台
    "your_platform": "your-domain.com"
}
```

---

## 📝 示例输出

### 输入

```python
{
    "platforms": ["github", "juejin"],
    "keywords": ["AI编程", "开源大模型"],
    "article_count_per_platform": 5
}
```

### 识别到的热点话题

```
1. AI编程工具与实践 (热度: 9.5)
   描述: 介绍AI编程技术发展、各类工具评测与工程化落地实践

2. 开源基础概念与普及 (热度: 8.0)
   描述: 讲解开源的定义、优势、常见误区

3. 国产大模型开源 (热度: 7.2)
   描述: 介绍国产顶尖大模型的开源进展

4. 开源许可证合规 (热度: 6.5)
   描述: 解析主流开源许可证的规则
```

### 生成的博客节选

> ## 从工具到协作伙伴：AI编程工具的技术演进、选型指南与工程化落地全指南
>
> 2023年GitHub Copilot正式商业化的时候，很多人还在吐槽它"经常生成错漏百出的代码"，到2024年我们团队做开发效率调研时，已经有超过70%的开发者日常工作中会使用至少一款AI编程工具...
>
> [完整文章已生成并导出为 PDF]

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 开源协议

本项目采用 MIT 开源协议，详情请参阅 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 工作流编排框架
- [Coze Coding SDK](https://github.com/coze-coding/coze-coding-dev-sdk) - 集成开发工具包
- 所有开源贡献者

---

## 📧 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/your-repo/issues)
- 发送邮件至：your-email@example.com

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star！**

Made with ❤️ by Tech Blog Generator Team

</div>
