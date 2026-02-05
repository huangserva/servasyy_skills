# Ultra Skill - AI 多媒体内容生产平台

AI驱动的多媒体内容生产平台。14个集成技能：document-writer（5种写作风格）、illustration-generator（20种配图风格）、ppt-generator（22种PPT风格）、podcast-generator（3种TTS引擎）、remotion-dev（视频制作）、twitter-crawler（推文爬取）、markdown-illustrator（Markdown配图）、comic-generator（漫画生成）、media-downloader（媒体下载）、tts-script-generator（TTS脚本）、md-to-pdf（文档转换）、wechat-formatter（微信格式化）、humanizer-zh（中文人性化）、shared-lib（核心API库）。

---

## 📋 技能列表

### 📝 内容创作类

#### 1. **document-writer** (48K)
多风格文档写作工具
- **功能**：支持 5 种写作风格（Qiaomu、小红书、Dankoe、微信公众号、Twitter）
- **特点**：Claude 智能选择风格，自动生成符合规范的文章
- **用途**：文章创作、内容营销、社交媒体发布

#### 2. **comic-generator** (76K)
知识漫画生成器
- **功能**：将文章/教程/人物传记转换为漫画形式
- **风格**：Ligne Claire、漫画教程风、武侠风等
- **用途**：知识可视化、教育内容

#### 3. **humanizer-zh** (8K)
中文文本人性化工具
- **功能**：使文本更自然、更人性化
- **用途**：文本优化、内容润色

---

### 🎨 图像生成类

#### 4. **illustration-generator** (48K)
统一配图技能
- **功能**：文章配图、封面生成、小红书图片系列
- **风格**：20 种风格 × 多种布局
- **特点**：3 变体风格预览、单图修改/添加/删除
- **用途**：文章配图、社交媒体图片

#### 5. **markdown-illustrator** (88K)
Markdown 文档配图工具
- **功能**：自动为 Markdown 文章生成配图
- **特点**：支持多种风格和布局、图片管理和优化
- **用途**：技术博客、文档美化

---

### 📊 演示文稿类

#### 6. **ppt-generator** (72K)
专业 PPT 生成器
- **功能**：生成专业 PPT 演示文稿
- **风格**：22 种风格（Apple、Minimal、Corporate、Blueprint、Notion 等）
- **布局**：17 种布局（封面、内容、对比、时间线等）
- **特点**：AI 自动选择最佳风格，支持场景/受众/调性智能匹配
- **用途**：商业汇报、技术演讲、教育培训

#### 7. **md-to-pdf** (8K)
Markdown 转 PDF 工具
- **功能**：将 Markdown 文档转换为 PDF
- **特点**：支持中文字体、可选自动配图、自定义样式
- **用途**：文档导出、报告生成

---

### 🎙️ 音频生成类

#### 8. **podcast-generator** (492K)
播客生成器
- **功能**：生成自然真实的双人访谈播客
- **引擎**：支持 3 种 TTS 引擎（Edge TTS、IndexTTS2、MiniMax、CosyVoice3）
- **特点**：情感控制、自然对话、多角色声音映射
- **用途**：播客制作、有声内容

#### 9. **tts-script-generator** (20K)
TTS 脚本生成器
- **功能**：智能压缩文档到目标时长，转换为 TTS 友好脚本
- **特点**：自动分段、情感标注、口语化风格
- **用途**：视频旁白、播客脚本

---

### 🎬 视频制作类

#### 10. **remotion-dev** (668K)
Remotion 视频制作工具
- **功能**：基于 React 的视频创作，支持高端品牌广告制作
- **特点**：30+ Remotion 最佳实践文档、完整工作流程
- **用途**：品牌广告、产品展示、视频动画

---

### 📥 媒体处理类

#### 11. **media-downloader** (188K)
智能媒体下载器
- **功能**：根据描述自动搜索下载图片/视频
- **来源**：YouTube、Pexels、Pixabay
- **特点**：自动视频剪辑、片段提取
- **用途**：素材收集、视频制作

#### 12. **twitter-crawler** (136K)
Twitter 推文爬取器
- **功能**：批量爬取用户推文、单条推文深度爬取
- **输出**：Markdown、JSON、XScore 格式
- **特点**：URL 智能解析、完整推文信息、媒体/实体提取
- **用途**：数据收集、内容分析、社交媒体研究

---

### 💬 格式化工具类

#### 13. **wechat-article-formatter** (4K)
微信公众号文章格式化工具
- **功能**：将 Markdown 文章转换为微信公众号 HTML 格式
- **特点**：自动插入配图、微信样式优化
- **用途**：微信公众号发布

---

### 🔧 核心库

#### 14. **shared-lib** (932K)
共享功能库
- **模块**：
  - `image_api.py` - 图像生成 API（支持多 provider）
  - `illustration/` - 配图风格系统（20 种风格）
  - `writing/` - 写作风格系统（5 种风格）
  - `presentation/` - PPT 生成系统
  - `video/` - 视频生成模块（TTS、动画、BGM）
- **配置**：新增 zimage 配置、servasyy 写作风格
- **用途**：所有技能的底层支持库

---

## 🏗️ 系统架构

### 核心设计原则

```
用户输入内容
    ↓
Claude AI 决策：
  - 判断内容类型（历史/技术/生活/商业）
  - 选择写作风格（wechat/qiaomu/xiaohongshu）
  - 选择配图风格（vintage/tech/warm）
  - 生成具体视觉描述
    ↓
shared-lib 执行：
  - 提供风格模板和规范
  - 分析文章结构、确定配图位置
  - 调用 API 生成内容
  - 处理音频和视频
```

### 职责分工

- **Claude AI**：内容理解、决策制定、风格选择
- **shared-lib**：模板提供、结构分析、API 调用
- **各技能**：专业化功能实现

---

## 📊 技能统计

| 类别 | 技能数量 | 总大小 |
|------|---------|--------|
| 内容创作 | 3 | 132K |
| 图像生成 | 2 | 136K |
| 演示文稿 | 2 | 80K |
| 音频生成 | 2 | 512K |
| 视频制作 | 1 | 668K |
| 媒体处理 | 2 | 324K |
| 格式化工具 | 1 | 4K |
| 核心库 | 1 | 932K |
| **总计** | **14** | **~2.8M** |

---

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+ (用于 Remotion)
- FFmpeg (用于视频处理)

### 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Node.js 依赖（如需使用 Remotion）
cd remotion-dev && npm install
```

### 配置

编辑 `shared-lib/config.yaml` 配置 API keys 和参数：

```yaml
# 图像生成配置
image_generation:
  default_provider: google-local
  providers:
    google-local:
      api_key: "your_api_key"
    
# TTS 配置
tts:
  default_engine: edge_tts
  
# 其他配置...
```

---

## 💡 使用示例

### 生成文章配图

```bash
# 使用 illustration-generator
python illustration-generator/generate.py article.md --style tech
```

### 生成 PPT

```bash
# 使用 ppt-generator
python ppt-generator/generate.py content.yaml --style apple
```

### 生成播客

```bash
# 使用 podcast-generator
python podcast-generator/generate.py script.txt --engine indextts2
```

### 爬取 Twitter

```bash
# 批量爬取用户推文
python twitter-crawler/scripts/fetch_tweets.py username

# 单条推文爬取
python twitter-crawler/scripts/fetch_single_tweet.py "https://x.com/user/status/123"
```

### 制作视频

```bash
# 使用 Remotion
cd remotion-dev
npm run render -- CompositionName output.mp4
```

---

## 📖 详细文档

- [系统完整说明](./MULTIMEDIA_SYSTEM_OVERVIEW.md) - 1040 行完整系统架构文档
- 各技能的 `SKILL.md` - 每个技能目录下的详细说明

---

## 🎯 核心能力

- ✍️ **多风格写作**：5 种专业写作风格，智能匹配场景
- 🎨 **20+ 配图风格**：从纽约客到浮世绘，覆盖各种场景
- 📊 **22 种 PPT 模板**：从商务到创意，自动选择最佳风格
- 🎙️ **3 种 TTS 引擎**：免费到商业，满足不同需求
- 🎬 **专业视频制作**：Remotion + 最佳实践，电影级质量
- 🐦 **Twitter 数据采集**：批量 + 单条，多格式输出
- 🔧 **统一 API 库**：shared-lib 提供底层支持

---

## 🌟 特色功能

### 1. 智能风格选择
Claude AI 自动分析内容，选择最合适的风格，无需手动配置。

### 2. 配置驱动
所有参数从 `config.yaml` 读取，用户无需修改代码。

### 3. 模块化设计
各技能独立运行，也可通过 shared-lib 协同工作。

### 4. 多格式输出
支持 Markdown、PDF、HTML、JSON、视频、音频等多种格式。

### 5. 生产级质量
所有技能经过实际项目验证，可直接用于生产环境。

---

## 🛠️ 技术栈

- **AI/ML**：Claude API、Whisper、各种图像生成 API
- **TTS**：Edge TTS、IndexTTS2、MiniMax、CosyVoice3
- **视频**：Remotion、FFmpeg、Manim
- **图像**：Google API、Z-Image、Volcengine、ApiMart
- **文档**：Python-PPTX、Markdown、Pandoc
- **爬虫**：Tweety、BeautifulSoup、HTTPX

---

## 📝 更新日志

### 2026-02-05
- ✅ 清理重复技能，从 36 个精简到 14 个
- ✅ 删除失效符号链接
- ✅ 清理虚拟环境和输出文件
- ✅ 目录大小从 5.7G 优化到 2.8M
- ✅ 更新 shared-lib（新增 zimage 配置和 servasyy 风格）
- ✅ 更新 ppt-generator（从 6 种风格扩展到 22 种）
- ✅ 更新 twitter-crawler（新增单条推文爬取功能）
- ✅ 更新 podcast-generator（新增 CosyVoice3 支持）

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 🔗 相关链接

- [Claude AI](https://claude.ai/)
- [Remotion](https://www.remotion.dev/)
- [Whisper](https://github.com/openai/whisper)

---

**最后更新**：2026-02-05
