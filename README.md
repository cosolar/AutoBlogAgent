# 🚀 AutoBlogAgent 技术博文自动生成智能体

> 基于 RSS 订阅源自动提取热门话题，智能搜索相关文章，生成专业完整的技术博客文档

[English](README_EN.md) | 中文

---

## 📖 项目简介

**AutoBlogAgent** 是一款基于 AI 的自动化技术博客生成工具。通过订阅多个 AI 技术 RSS 源，自动提取热门话题，然后使用搜索引擎抓取相关文章，利用大语言模型分析识别技术热点，并自动生成结构完整、内容专业的技术博客文章，最终导出为可下载的 PDF 文档。

### 核心特性

- 📡 **多 RSS 订阅源** - 支持 Infinitum AI 日报、AI Hot 等多个订阅源
- 🔍 **智能话题提取** - 自动从 RSS 解析热门关键词和话题
- 🌐 **百度搜索** - 基于话题自动搜索相关文章
- 🧠 **AI 热点识别** - 使用大语言模型智能分析，识别技术热点话题
- ✍️ **自动博客生成** - 生成结构清晰、内容专业的技术博客文章
- 📄 **PDF 文档导出** - 一键生成可分享的 PDF 文档

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AutoBlogAgent 技术博客生成工作流                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐    │
│  │   RSS 订阅      │───▶│   文章搜索      │───▶│   热点分析      │    │
│  │ rss_subscription│    │ article_fetch  │    │hot_topic_analysis│    │
│  └────────────────┘    └────────────────┘    └────────────────┘    │
│                                                           │          │
│                                                           ▼          │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐    │
│  │   文档生成      │◀───│   博客生成      │◀───│   话题选择      │    │
│  │document_generation│  │ blog_generation│    │ topic_selection │    │
│  └────────────────┘    └────────────────┘    └────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 工作流节点说明

| 节点名称 | 类型 | 功能描述 |
|---------|------|---------|
| `rss_subscription` | Task | 从多个 RSS 订阅源获取热门话题 |
| `article_fetch` | Task | 基于话题使用百度搜索抓取相关文章 |
| `hot_topic_analysis` | Agent | 使用 LLM 分析文章，识别热点话题 |
| `topic_selection` | Task | 从多个热点中选择最热门的话题 |
| `blog_generation` | Agent | 基于热点话题生成完整的技术博客 |
| `document_generation` | Task | 将博客转换为 PDF 文档 |

---

## 🎯 功能详解

### 0. RSS 订阅话题获取

支持从多个 RSS 订阅源自动获取热门话题：

| 订阅源 | URL | 说明 |
|-------|-----|------|
| Infinitum AI 日报 | `http://infinitum.shawnxie.top/api/daily/rss` | AI 技术每日热点 |
| AI Hot | `https://aihot.virxact.com/feed/all.xml` | AI 热点资讯 |

**特性：**
- 并行获取多个 RSS 源，提升效率
- 智能提取标题和描述中的关键词
- 自动去重和热度排序
- 支持自定义 RSS 订阅源列表

### 1. 基于话题的文章搜索

使用百度搜索基于 RSS 话题抓取相关文章：

**搜索策略：**
- 直接使用 RSS 提取的热门话题作为搜索关键词
- 智能构建搜索查询，确保搜索结果相关性
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
- **大语言模型**: 支持多种模型（Coze SDK / OpenAI / 阿里百炼 / DeepSeek / Kimi 等）
- **文章搜索**: Web Search API
- **文档生成**: PDF Generation API
- **提示词模板**: Jinja2

### 支持的 LLM 提供商

本项目使用统一的 LLM 客户端 (`src/utils/llm_client.py`)，支持多种大语言模型提供商：

| 提供商 | 类型 | 模型示例 | 说明 |
|--------|------|---------|------|
| **Coze SDK** | `coze` | doubao-seed-2-0-pro | 通过 Coze 平台调用豆包模型 |
| **OpenAI** | `openai` | gpt-4o, gpt-4-turbo | OpenAI 官方 API |
| **阿里百炼** | `dashscope` | qwen-plus, qwen-max | 阿里云通义千问系列 |
| **DeepSeek** | `deepseek` | deepseek-chat, deepseek-coder | DeepSeek 模型 |
| **Kimi** | `kimi` | moonshot-v1-8k, moonshot-v1-32k | 月之暗面 Kimi 模型 |

> 💡 **提示**: 所有支持的模型列表可参考 [LLM Skill 文档](/skills/public/prod/llm)

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
│   ├── utils/                    # 工具模块
│   │   └── llm_client.py        # 通用 LLM 客户端（支持多模型）
│   └── main.py                   # 程序入口
├── config/                       # 配置文件
│   ├── hot_topic_analysis_llm_cfg.json
│   ├── blog_generation_llm_cfg.json
│   └── examples/                # 配置示例
│       ├── coze_example.json
│       ├── openai_example.json
│       ├── dashscope_example.json
│       ├── deepseek_example.json
│       └── kimi_example.json
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
# 一键推送到 GitHub
chmod +x scripts/push_to_github.sh
./scripts/push_to_github.sh <你的GitHub_Token> <仓库名称> [仓库描述]

# 示例
./scripts/push_to_github.sh ghp_xxxxxxxxxxxxxxx tech-blog-generator "技术热点追踪与博客生成"

# 获取 GitHub Token:
# 1. 登录 GitHub → Settings → Developer settings
# 2. Personal access tokens → Generate new token
# 3. 勾选 repo 权限 → 生成并复制
```

### 运行工作流

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

### 多模型支持说明

本项目采用统一的 LLM 客户端架构，通过配置文件中的 `type` 字段指定模型类型，支持以下模型提供商：

#### 1. Coze SDK (豆包模型)

通过 Coze 平台调用豆包系列模型，适合国内用户：

```json
{
    "type": "coze",
    "config": {
        "model": "doubao-seed-2-0-pro-260215",
        "temperature": 0.7,
        "max_completion_tokens": 8000
    },
    "sp": "你是一个专业的技术博客写作助手...",
    "up": "根据以下文章内容分析技术热点..."
}
```

**适用场景**: 国内用户、需要稳定服务的生产环境

#### 2. OpenAI GPT 系列

使用 OpenAI 官方 API：

```json
{
    "type": "openai",
    "config": {
        "model": "gpt-4o",
        "api_key": "your-openai-api-key",
        "temperature": 0.7,
        "max_tokens": 8000
    },
    "sp": "You are a professional technical blog writer...",
    "up": "Analyze the following articles and identify hot topics..."
}
```

**适用场景**: 国际化项目、已有 OpenAI API 的团队

#### 3. 阿里百炼 (通义千问)

使用阿里云百炼平台：

```json
{
    "type": "dashscope",
    "config": {
        "model": "qwen-plus",
        "api_key": "your-dashscope-api-key",
        "temperature": 0.7,
        "max_tokens": 8000
    },
    "sp": "你是一个专业的技术博客写作助手...",
    "up": "根据以下文章内容分析技术热点..."
}
```

**适用场景**: 阿里云用户、国内企业、对数据安全有要求的场景

#### 4. DeepSeek

使用 DeepSeek 模型：

```json
{
    "type": "deepseek",
    "config": {
        "model": "deepseek-chat",
        "api_key": "your-deepseek-api-key",
        "temperature": 0.7,
        "max_tokens": 8000
    },
    "sp": "You are a professional technical blog writer...",
    "up": "Analyze the following articles and identify hot topics..."
}
```

**适用场景**: 追求性价比、需要代码能力强的模型

#### 5. Kimi (月之暗面)

使用月之暗面 Kimi 模型：

```json
{
    "type": "kimi",
    "config": {
        "model": "moonshot-v1-8k",
        "api_key": "your-kimi-api-key",
        "temperature": 0.7,
        "max_tokens": 8000
    },
    "sp": "你是一个专业的技术博客写作助手...",
    "up": "根据以下文章内容分析技术热点..."
}
```

**适用场景**: 长文本处理、长文档分析场景

### 配置文件模板

配置文件位于 `config/` 目录，必须包含以下字段：

```json
{
    "type": "coze|openai|dashscope|deepseek|kimi",  // 模型类型
    "config": {
        "model": "model-id",        // 模型 ID
        "temperature": 0.7,         // 温度参数 (0-1)
        "max_tokens": 8000          // 最大 token 数
        // 其他参数...
    },
    "sp": "系统提示词",
    "up": "用户提示词 (支持 Jinja2 模板)"
}
```

### 快速切换模型

只需修改 `config/*.json` 中的配置，即可切换不同的模型：

```python
# 使用 Coze SDK
# config: "type": "coze", "model": "doubao-seed-2-0-pro-260215"

# 切换到 OpenAI
# config: "type": "openai", "model": "gpt-4o"

# 切换到阿里百炼
# config: "type": "dashscope", "model": "qwen-plus"
```

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
