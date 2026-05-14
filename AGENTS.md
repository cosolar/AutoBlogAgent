# AutoBlogAgent 技术博文自动生成智能体

## 项目概述
- **名称**: AutoBlogAgent
- **功能**: 订阅Infinitum AI日报获取热门话题，调用大模型生成AI技术话题，并行追踪GitHub、掘金、CSDN、博客园等开源技术平台的热点文章，识别热点话题，自动生成专业完整的技术博客文档

### 节点清单

| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| rss_subscription | `nodes/rss_subscription_node.py` | task | 从Infinitum AI日报订阅源获取热门话题 | - | fetch-url技能 |
| article_fetch | `nodes/article_fetch_node.py` | task | 合并RSS话题 + LLM生成话题，并行多平台抓取热门文章 | - | `topic_generation_llm_cfg.json`, Web搜索技能 |
| hot_topic_analysis | `nodes/hot_topic_analysis_node.py` | agent | 使用LLM分析文章并识别热点话题 | - | `config/hot_topic_analysis_llm_cfg.json` |
| topic_selection | `nodes/topic_selection_node.py` | task | 从热点话题中选择最热门主题 | - | - |
| blog_generation | `nodes/blog_generation_node.py` | agent | 基于热点话题生成技术博客 | - | `config/blog_generation_llm_cfg.json` |
| document_generation | `nodes/document_generation_node.py` | task | 将博客转换为PDF文档 | - | 文档生成技能 |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
本工作流不包含子图，所有节点均在主图中顺序执行。

## 技能使用
- 节点`rss_subscription`：
  - 使用**fetch-url**技能从多个RSS订阅源并行获取热门话题
  - 默认订阅源：
    - Infinitum AI 日报 (http://infinitum.shawnxie.top/api/daily/rss)
    - AI Hot (https://aihot.virxact.com/feed/all.xml)
  - 支持自定义RSS订阅源列表
- 节点`article_fetch`：
  - 优先使用RSS话题，如果RSS获取失败则使用**大语言模型**技能生成AI技术话题
  - 使用**Web搜索**技能从GitHub、掘金、CSDN、博客园等平台抓取文章（并行搜索）
- 节点`hot_topic_analysis`使用**大语言模型**技能分析热点话题
- 节点`blog_generation`使用**大语言模型**技能生成博客文章
- 节点`document_generation`使用**文档生成**技能生成PDF文档

## 工作流输入参数

| 参数名 | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| platforms | List[str] | ["github", "juejin", "csdn", "cnblogs"] | 要抓取的技术平台列表 |
| keywords | List[str] | ["开源", "AI", "编程", "技术趋势"] | 搜索关键词（当RSS不可用时使用） |
| article_count_per_platform | int | 10 | 每个平台抓取的文章数量 |
| rss_url | str | "http://infinitum.shawnxie.top/api/daily/rss" | RSS订阅链接 |

## 工作流输出

| 字段 | 类型 | 说明 |
|-----|------|------|
| hot_topics | List[HotTopic] | 识别的热点话题列表 |
| blog_content | BlogContent | 生成的博客内容 |
| document_url | str | 生成的PDF文档下载链接 |
| rss_topics | List[str] | 从RSS订阅提取的热门话题 |
| daily_topics | List[DailyTopic] | 每日话题详情 |
