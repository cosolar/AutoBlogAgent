# 🚀 Tech Blog Generator - Intelligent Tech Blog Generator

> Automatically track trending articles from GitHub, Juejin, CSDN, CNBlogs and other tech platforms, intelligently identify hot topics, and generate professional technical blog documents

[English](README.md) | 中文

---

## 📖 Project Overview

**Tech Blog Generator** is an AI-powered automated technical blog generation tool. It can automatically fetch trending articles from multiple mainstream tech platforms, use large language models to analyze and identify the hottest technical topics, and automatically generate complete, professionally structured technical blog articles, ultimately exporting them as downloadable PDF documents.

### Key Features

- 🔍 **Multi-Platform Article Fetching** - Support for GitHub, Juejin, CSDN, CNBlogs and other mainstream tech platforms
- 🧠 **AI Hot Topic Identification** - Use LLM to intelligently analyze and identify technical hot topics
- ✍️ **Automatic Blog Generation** - Generate well-structured, professionally written technical blogs
- 📄 **PDF Document Export** - One-click generation of shareable PDF documents
- ⚙️ **Highly Customizable** - Support custom search keywords, platform selection, article count and more

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Tech Blog Generator Workflow                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Article    │───▶│    Hot      │───▶│    Topic     │      │
│  │   Fetch      │    │    Topic    │    │  Selection   │      │
│  │              │    │  Analysis   │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                  │               │
│                                                  ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Document   │◀───│    Blog     │◀───│    Blog      │      │
│  │  Generation  │    │  Generation │    │  Generation  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Nodes

| Node Name | Type | Description |
|-----------|------|-------------|
| `article_fetch` | Task | Fetch trending articles from specified tech platforms |
| `hot_topic_analysis` | Agent | Analyze articles using LLM to identify hot topics |
| `topic_selection` | Task | Select the hottest topic from multiple options |
| `blog_generation` | Agent | Generate complete technical blog based on hot topic |
| `document_generation` | Task | Convert blog to PDF document |

---

## 🎯 Features

### 1. Multi-Platform Article Fetching

Supports fetching trending articles from the following tech platforms:

| Platform | Domain | Description |
|----------|--------|-------------|
| GitHub | github.com | Trending open source projects and dev discussions |
| Juejin | juejin.cn | Leading tech community in China |
| CSDN | csdn.net | Veteran programmer tech community |
| CNBlogs | cnblogs.com | Senior developer blog platform |

**Fetching Strategy:**
- Support multi-keyword parallel search
- Automatic deduplication for article uniqueness
- Smart extraction of article title, abstract, publication time and more

### 2. AI Hot Topic Identification

Use large language models for deep analysis of fetched articles:

```
Input: 20-30 tech articles
       ↓
AI Analysis:
  - Extract key technical topic words
  - Count topic frequency
  - Evaluate topic heat score
       ↓
Output: List of 3-5 hot topics
        Each topic includes:
        - Topic name
        - Topic description
        - Related article list
        - Heat score (0-10)
```

### 3. Smart Topic Selection

- Automatically select the highest-scoring topic
- Support generating corresponding tech blog for each topic
- Keep all identified hot topics for reference

### 4. Professional Blog Generation

Generated blogs include complete article structure:

```markdown
# Article Title

> Auto-generated tech blog | Based on hot topic analysis

---

## Introduction
## Topic Overview
## Technical Details/Core Principles
## Practical Applications/Case Studies
## Summary and Outlook
## References
```

**Blog Features:**
- Written in Chinese, matching domestic developer reading habits
- Clear structure, rigorous logic
- Professional but not obscure content
- Usually 1500+ words
- Includes complete reference links

### 5. PDF Document Export

- Automatically convert blog to professional PDF document
- Chinese font support
- Auto-generated table of contents
- Directly downloadable and shareable

---

## 🛠️ Tech Stack

### Core Technologies

- **Workflow Orchestration**: LangGraph
- **Large Language Model**: Doubao Seed / DeepSeek / Kimi
- **Article Search**: Web Search API
- **Document Generation**: PDF Generation API

### Development Framework

```
Python >= 3.10
├── langgraph          # Workflow orchestration framework
├── langchain-core     # Message passing and tool definitions
├── coze-coding-dev-sdk # Integration SDK
└── pydantic           # Data validation
```

### Project Structure

```
├── src/
│   ├── graphs/                    # Workflow core code
│   │   ├── state.py              # Global state definitions
│   │   ├── graph.py              # Main graph orchestration
│   │   └── nodes/                # Node implementations
│   │       ├── article_fetch_node.py
│   │       ├── hot_topic_analysis_node.py
│   │       ├── topic_selection_node.py
│   │       ├── blog_generation_node.py
│   │       └── document_generation_node.py
│   └── main.py                   # Program entry
├── config/                       # Configuration files
│   ├── hot_topic_analysis_llm_cfg.json
│   └── blog_generation_llm_cfg.json
├── tests/                        # Test cases
├── AGENTS.md                     # Project spec document
└── README.md                     # Project documentation
```

---

## 🚀 Quick Start

### Requirements

- Python 3.10+
- Internet connection (for accessing search API)

### Installation

```bash
# Install dependencies using uv (recommended)
uv sync

# Or use pip
pip install -r requirements.txt
```

### Basic Usage

```python
from src.graphs.graph import main_graph

# Define workflow input
input_data = {
    "platforms": ["github", "juejin", "csdn", "cnblogs"],  # Platforms to fetch from
    "keywords": ["open source", "AI", "programming", "tech trends"],  # Search keywords
    "article_count_per_platform": 10                        # Article count per platform
}

# Execute workflow
result = main_graph.invoke(input_data)

# Get results
print("Identified hot topics:", result["hot_topics"])
print("Generated blog:", result["blog_content"]["title"])
print("Document download URL:", result["document_url"])
```

### Parameter Description

| Parameter | Type | Required | Default | Description |
|:---------:|:----:|:--------:|:-------:|:------------|
| `platforms` | List[str] | No | `["github", "juejin", "csdn", "cnblogs"]` | Tech platforms to fetch from |
| `keywords` | List[str] | No | `["open source", "AI", "programming", "tech trends"]` | Search keyword list |
| `article_count_per_platform` | int | No | `10` | Article count per platform |

### Output Structure

```python
{
    "hot_topics": [
        {
            "topic": "AI Programming Tools and Practices",
            "description": "Introduction to AI programming tech development...",
            "related_articles": ["Article 1", "Article 2", ...],
            "heat_score": 9.5
        },
        ...
    ],
    "blog_content": {
        "title": "Article Title",
        "outline": ["Introduction", "Topic Overview", ...],
        "content": "# Markdown formatted article content",
        "references": ["url1", "url2", ...]
    },
    "document_url": "https://xxx.pdf"
}
```

---

## 💡 Use Cases

### 1. Tech Bloggers

Quickly get the latest tech trends and generate blog drafts to improve content creation efficiency.

### 2. Tech Teams

Generate regular tech trend reports to help teams understand industry developments.

### 3. Content Operations

Automatically generate tech content for WeChat public accounts, tech communities and other content distribution channels.

### 4. Personal Learning

Track interesting tech fields and generate learning notes and summaries.

---

## 🔧 Advanced Configuration

### Custom LLM Configuration

Edit JSON config files in `config/` directory:

```json
{
    "config": {
        "model": "doubao-seed-2-0-pro-260215",
        "temperature": 0.7,
        "max_completion_tokens": 8000
    },
    "sp": "Your system prompt...",
    "up": "Your user prompt..."
}
```

### Supported Models

| Model ID | Description |
|----------|-------------|
| `doubao-seed-2-0-pro-260215` | Flagship all-round model, suitable for complex tasks |
| `doubao-seed-2-0-lite-260215` | Balanced model, high cost-effectiveness |
| `deepseek-v3-2-251201` | DeepSeek V3.2 model |
| `kimi-k2-5-260127` | Kimi K2.5 model |

### Custom Search Platforms

Modify `platform_domains` in `article_fetch_node.py`:

```python
platform_domains = {
    "github": "github.com",
    "juejin": "juejin.cn",
    "csdn": "csdn.net",
    "cnblogs": "cnblogs.com",
    # Add custom platform
    "your_platform": "your-domain.com"
}
```

---

## 📝 Example Output

### Input

```python
{
    "platforms": ["github", "juejin"],
    "keywords": ["AI programming", "open source LLMs"],
    "article_count_per_platform": 5
}
```

### Identified Hot Topics

```
1. AI Programming Tools and Practices (Heat: 9.5)
   Description: Introduction to AI programming tech development, tool reviews and engineering practices

2. Open Source Basics and Popularization (Heat: 8.0)
   Description: Explaining open source definition, advantages, common misconceptions

3. Domestic LLM Open Source (Heat: 7.2)
   Description: Introduction to domestic top LLM open source progress

4. Open Source License Compliance (Heat: 6.5)
   Description: Analyzing mainstream open source license rules
```

### Generated Blog Excerpt

> ## From Tool to Collaborative Partner: A Complete Guide to AI Programming Tools - Technical Evolution, Selection Guide and Engineering Implementation
>
> When GitHub Copilot was officially commercialized in 2023, many people were still complaining about its "code full of errors"... by 2024, our team found that over 70% of developers use at least one AI programming tool in their daily work...
>
> [Full article generated and exported as PDF]

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow orchestration framework
- [Coze Coding SDK](https://github.com/coze-coding/coze-coding-dev-sdk) - Integration development toolkit
- All open source contributors

---

## 📧 Contact

For questions or suggestions, feel free to contact:

- Submit [GitHub Issue](https://github.com/your-repo/issues)
- Send email: your-email@example.com

---

<div align="center">

**If this project is helpful to you, please give a ⭐ Star!**

Made with ❤️ by Tech Blog Generator Team

</div>
