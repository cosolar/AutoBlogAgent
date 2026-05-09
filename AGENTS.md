# 技术热点追踪与博客生成工作流

## 项目概述
- **名称**: Tech Blog Generator
- **功能**: 自动追踪GitHub、掘金、CSDN、博客园等开源技术平台的热点文章，识别热点话题，并生成专业完整的技术博客文档

### 节点清单

| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| article_fetch | `nodes/article_fetch_node.py` | task | 从多平台抓取热门文章数据 | - | Web搜索技能 |
| hot_topic_analysis | `nodes/hot_topic_analysis_node.py` | agent | 使用LLM分析文章并识别热点话题 | - | `config/hot_topic_analysis_llm_cfg.json` |
| topic_selection | `nodes/topic_selection_node.py` | task | 从热点话题中选择最热门主题 | - | - |
| blog_generation | `nodes/blog_generation_node.py` | agent | 基于热点话题生成技术博客 | - | `config/blog_generation_llm_cfg.json` |
| document_generation | `nodes/document_generation_node.py` | task | 将博客转换为PDF文档 | - | 文档生成技能 |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
本工作流不包含子图，所有节点均在主图中顺序执行。

## 技能使用
- 节点`article_fetch`使用**Web搜索**技能从GitHub、掘金、CSDN、博客园等平台抓取文章
- 节点`hot_topic_analysis`使用**大语言模型**技能分析热点话题
- 节点`blog_generation`使用**大语言模型**技能生成博客文章
- 节点`document_generation`使用**文档生成**技能生成PDF文档

## 工作流输入参数

| 参数名 | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| platforms | List[str] | ["github", "juejin", "csdn", "cnblogs"] | 要抓取的技术平台列表 |
| keywords | List[str] | ["开源", "AI", "编程", "技术趋势"] | 搜索关键词 |
| article_count_per_platform | int | 10 | 每个平台抓取的文章数量 |

## 工作流输出

| 字段 | 类型 | 说明 |
|-----|------|------|
| hot_topics | List[HotTopic] | 识别的热点话题列表 |
| blog_content | BlogContent | 生成的博客内容 |
| document_url | str | 生成的PDF文档下载链接 |
