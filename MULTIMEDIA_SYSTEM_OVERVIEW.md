# 多媒体内容生产平台 - 完整系统说明

## 📋 系统概览

这是一个完整的**多媒体内容生产平台**，支持从文档到文章、图片、音频、视频的全自动生产流程。

**核心能力：**
- 📝 文章撰写（Qiaomu 风格解读）
- 🎨 图像生成（纽约客/浮世绘等多种风格）
- 🎤 音频生成（TTS + 播客）
- 🎬 视频生成（智能动画 + 字幕）
- 📱 多平台发布（微信/抖音/小红书）

---

## 🧠 核心设计原则

### 职责分工：Claude 决策 + shared-lib 执行

```
用户输入内容
    ↓
Claude 阅读内容，做出决策：
  - 判断内容类型（历史/技术/生活/商业...）
  - 选择写作风格（wechat/qiaomu/xiaohongshu...）
  - 选择配图风格（vintage/tech/warm...）
  - 生成具体视觉描述（而非通用模板）
    ↓
调用 shared-lib 模块执行：
  - writing/ → 提供风格模板和规范
  - illustration/ → 分析文章结构、确定配图位置
  - image_api.py → 生成图片
  - video/ → 生成音频和视频
```

### 关键原则

1. **Claude 负责决策**：内容类型判断、风格选择、视觉描述生成
2. **shared-lib 负责执行**：提供模板规范、分析结构、调用API
3. **不做穷举**：不依赖关键词库判断内容类型，由 Claude 智能理解
4. **配置驱动**：优先级、参数等从 `config.yaml` 读取，用户无需改代码

---

## 🏗️ 系统架构

### 1. 共享库 (`~/.claude/skills/shared-lib/`)

```
shared-lib/
├── image_api.py          # 图像生成 API
│   ├── 支持多个 provider（google-local, z-image, volcengine, apimart）
│   └── 自动降级机制
│
├── bgm/                  # BGM 预设音乐目录
│   └── (用户放置 mp3/wav 文件)
│
├── illustration/         # 配图风格系统（新增）
│   ├── generator.py      # IllustrationGenerator（20种风格×5种布局）
│   ├── xhs_generator.py  # 小红书专用生成器
│   ├── styles/           # 20种风格定义
│   │   ├── newyorker.yaml, ukiyoe.yaml, tech.yaml...
│   │   └── elegant.yaml, minimal.yaml, cute.yaml...
│   ├── layouts/          # 5种通用布局
│   │   └── single.yaml, infographic.yaml, comparison.yaml...
│   └── xhs/              # 小红书专用布局（6种）
│       └── layout_sparse.yaml, layout_balanced.yaml...
│
├── writing/              # 写作风格系统（新增）
│   ├── generator.py      # WritingStyleGenerator
│   └── styles/           # 5种写作风格
│       ├── qiaomu.yaml   # 乔木体（8000-10000字）
│       ├── xiaohongshu.yaml # 小红书体（800-1200字）
│       ├── dankoe.yaml   # Dan Koe体（5000-8000字）
│       ├── wechat.yaml   # 微信公众号体（3000-6000字）
│       └── twitter.yaml  # 推特体（100-280字）
│
├── presentation/         # PPT生成系统（新增）
│   ├── generator.py      # PresentationGenerator
│   ├── styles/           # 6种PPT风格
│   ├── layouts/          # 5种布局
│   └── themes/           # 8种主题
│
└── video/                # 视频生成模块
    ├── tts/              # TTS 音频生成
    │   ├── edge_tts.py   # Edge TTS（免费）
    │   ├── indextts2.py  # IndexTTS2（声音克隆）
    │   ├── minimax.py    # MiniMax（商业API）
    │   └── factory.py    # 统一接口
    │
    ├── animation/        # 文本动画
    │   └── animator.py   # Manim 动画器（4种风格，3种尺寸）
    │
    ├── bgm.py            # BGM 背景音乐模块
    │   ├── add_bgm_to_video() - 添加BGM
    │   ├── 支持循环、淡入淡出
    │   └── 动态音频归一化
    │
    ├── templates.py      # 视频模板系统
    │   ├── load_template() - 加载模板
    │   ├── list_templates() - 列出可用模板
    │   └── get_template_style() - 获取样式配置
    │
    ├── templates/        # 模板定义目录
    │   ├── 9x16/         # 竖屏（抖音）
    │   │   ├── default.yaml
    │   │   ├── elegant.yaml
    │   │   └── minimal.yaml
    │   ├── 16x9/         # 横屏（B站）
    │   │   ├── default.yaml
    │   │   └── cinematic.yaml
    │   └── 1x1/          # 方形（小红书）
    │       └── card.yaml
    │
    └── manim_composer.py # Manim 视频合成器
        ├── 透明背景动画 + 背景图叠加
        ├── 手写字幕效果（Write动画）
        ├── 多尺寸支持（16:9/9:16/1:1）
        ├── BGM 集成
        └── 自动音频同步
```

---

## 🎯 核心 Skills 体系

### 📝 文本生产层

#### 1. servasyy-document-interpreter ⚠️ 暂不使用
**职责：** 文档 → Qiaomu 风格文章

**状态：** 🚫 暂时停用，文章撰写请使用 `document-writer` 或手动撰写

**输入：** PDF / Word / HTML / URL / Markdown
**输出：** 
- Markdown 文章（8000-10000字）
- WeChat HTML
- PowerPoint（13种风格）

**特点：**
- 对话式语言
- 术语解释
- 生活化类比

**使用：**
```
解读 paper.pdf
```

---

#### 1.5 document-writer（新增）
**职责：** 多风格文章撰写 + 智能分析 + 风格转换

**5种写作风格：**
| 风格 | 字数 | 特点 |
|------|------|------|
| qiaomu | 8000-10000 | 深度解读，对话式 |
| xiaohongshu | 800-1200 | 种草风，emoji多 |
| dankoe | 5000-8000 | 思想领袖，简洁有力 |
| wechat | 3000-6000 | 公众号风，段落短 |
| twitter | 100-280 | 推特风，金句为主 |

**智能分析（新增）：**
- 内容类型识别（技术教程/产品评测/观点输出...）
- 目标受众识别
- 平台适配度（微信/小红书/Twitter/知乎/Newsletter）
- 写作要点建议

**风格转换（新增）：**
```bash
# 长文转小红书
/document-writer convert article.md --to xiaohongshu

# 长文转推特线程
/document-writer convert article.md --to twitter
```

---

#### 1.6 ppt-generator（新增）
**职责：** PPT 生成

**特点：**
- **22种PPT风格**（详见下表）
- **15种布局**（cover, section_divider, content_left, content_center, content_two_column, title_hero, key_stat, quote_callout, icon_grid, three_columns, timeline, comparison, hub_spoke, pyramid, agenda）
- **8种主题配色**（仅 apple 风格支持）

**22种风格分类：**

| 梯队 | 风格 | 质量 | 适用场景 |
|------|------|------|----------|
| 第一梯队 | `apple`, `minimal`, `corporate` | 9-10 | 科技/商务/高管汇报 |
| 第二梯队 | `blueprint`, `notion`, `scientific`, `editorial`, `editorial_infographic`, `intuition_machine` | 8 | 技术架构/学术/数据 |
| 第三梯队 | `sketch_notes`, `chalkboard`, `fantasy_animation` | 7-8 | 教育/培训/儿童 |
| 第四梯队 | `watercolor`, `vector_illustration`, `dark_atmospheric`, `bold_editorial`, `storytelling` | 7-8 | 创意/艺术/营销 |
| 第五梯队 | `pixel_art`, `vintage`, `neumorphism`, `material`, `fluent` | 6-7 | 游戏/历史/特色 |

**使用：**
```bash
/ppt-generator article.md --style apple
/ppt-generator article.md --style vintage  # 历史类内容
/ppt-generator article.md --style sketch_notes  # 教程类内容
```

---

#### 2. tts-script-generator
**职责：** 文章 → TTS 脚本 + 智能动画标记

**输入：** Markdown 文章
**输出：** 
- `tts_script.json`（含动画标记）
- `visual_config.json`（配图描述）

**智能决策：**
- 开场 → `fade_in`
- 核心观点 → `write`
- 数据/事实 → `typewriter`
- 普通内容 → `none`（ASS字幕）

**使用：**
```
生成 TTS 脚本 article.md
```

---

### 🎨 图像生产层

#### 3. illustration-generator
**职责：** 统一配图生成（文章配图、封面、小红书图片系列）

**特点：**
- **20种风格**（newyorker, ukiyoe, tech, notion, warm, flat, watercolor + 13种新增）
- **5种通用布局**（single, infographic, comparison, flow, scene）
- **小红书分支**：6种专用布局 + 内容分析 + Hook识别
- 并行生成（4线程）
- MD5 缓存机制
- 3变体风格预览

**20种风格分类：**
| 分类 | 风格 |
|------|------|
| 经典 | newyorker, ukiyoe |
| 科技 | tech, blueprint, pixel-art |
| 极简 | notion, minimal, flat |
| 温暖 | warm, playful, cute |
| 艺术 | watercolor, sketch |
| 复古 | vintage, retro |
| 专业 | elegant, scientific, editorial |
| 教育 | chalkboard |
| 自然 | nature |

**小红书模式：**
```bash
# 小红书图片系列
/illustration-generator content.md --mode xhs --style cute --count 5
```

**小红书布局：**
| 布局 | 密度 | 使用场景 |
|------|------|---------|
| sparse | 1-2点 | 封面、金句 |
| balanced | 3-4点 | 常规内容 |
| dense | 5-8点 | 知识卡片 |
| list | 4-7项 | 清单、排名 |
| comparison | 2侧 | 优缺点对比 |
| flow | 3-6步 | 流程、步骤 |

**使用：**
```bash
# 文章配图
/illustration-generator article.md

# 指定风格
/illustration-generator article.md --style tech

# 小红书模式
/illustration-generator content.md --mode xhs
```

---

#### 3.5 comic-generator（新增）
**职责：** 知识漫画生成

**特点：**
- 9种漫画风格（classic, ohmsha, dramatic, warm, sepia, vibrant, realistic, wuxia, shoujo）
- 6种页面布局（standard, cinematic, dense, splash, mixed, webtoon）
- 3种比例（3:4, 4:3, 16:9）
- 自动内容分析→角色设计→分镜→生成

**使用：**
```bash
/comic-generator article.md --style ohmsha --layout dense
```

---

### 🎤 音频生产层

#### 4. podcast-generator
**职责：** 生成双人访谈播客

**特点：**
- 使用 `video.tts` 模块
- 支持情感控制（9种情感）
- 自动音频合成

**输入：** 播客脚本（角色|情感|文本）
**输出：** MP3 音频

**使用：**
```
生成播客 script.txt
```

---

### 🎬 视频生产层

#### 5. image-to-video
**职责：** 图片 + 音频 → 视频

**核心脚本：**
- `generate_tts_v2.py` - 生成 TTS 音频
- `compose_smart.py` - 智能合成视频

**特点：**
- **默认 9:16 竖屏**（抖音/小红书）
- Claude 智能决策（Manim vs ASS）
- 并行处理（4线程）
- 自动降级机制

**使用：**
```bash
# 生成音频
python generate_tts_v2.py

# 合成视频（默认 9:16）
python compose_smart.py

# 或 16:9
python compose_smart.py --aspect-ratio 16:9
```

---

#### 5.1 manim_composer（新增）
**职责：** Manim 手写字幕 + 背景图 + 音频 → 完整视频段

**核心功能：**
- 🎨 **透明背景动画**：Manim 生成 .mov 格式（支持 alpha 通道）
- ✍️ **手写效果**：Write 动画，书法感字幕
- 🖼️ **背景叠加**：FFmpeg 将动画叠加到背景图上
- 🔊 **音频同步**：自动匹配音频时长

**字幕样式：**
- 字体：Heiti SC（黑体）
- 字号：80px
- 字重：ULTRABOLD（超粗）
- 颜色：白色 (#FFFFFF)
- 描边：2px 黑色细边框
- 位置：底部 10%（shift DOWN * 8.8）
- 自动缩放：宽度超过 85% 时自动缩小

**使用：**
```python
from video.manim_composer import create_manim_video_segment

result = create_manim_video_segment(
    text="这是手写字幕效果",
    image_path="background.png",
    audio_path="audio.mp3",
    animation_style='write',  # fade_in, write, typewriter, slide_in
    output_path="output.mp4"
)
```

**批量生成脚本：**
```bash
# 基础用法
python ~/generate_manim_video.py <字幕目录> <图片目录> <音频目录> <输出文件>

# 添加BGM
python ~/generate_manim_video.py ... output.mp4 --bgm relaxing

# 横屏视频
python ~/generate_manim_video.py ... output.mp4 --aspect 16:9

# 完整示例
python ~/generate_manim_video.py qin_army_segments qin_army_illustrations qin_army_audio output.mp4 --bgm emotional --aspect 9:16
```

---

#### 5.2 BGM 背景音乐
**职责：** 为视频添加背景音乐

**预设风格：**
- `upbeat` - 轻快欢乐，适合科普、生活类
- `epic` - 史诗震撼，适合历史、纪录片
- `emotional` - 感人温暖，适合人文故事
- `relaxing` - 舒缓平静，适合冥想、自然
- `corporate` - 商务专业，适合科技、商业

**使用：**
```python
from video.bgm import add_bgm_to_video

add_bgm_to_video(
    video_path="video.mp4",
    bgm_path="relaxing",      # 预设风格或文件路径
    output_path="output.mp4",
    bgm_volume=0.3,           # 音量 (0.0-1.0)
    loop=True,                # 循环播放
    fade_out=2.0              # 淡出时长
)
```

**自定义BGM：**
将 mp3/wav 文件放入 `~/.claude/skills/shared-lib/bgm/` 目录

---

#### 5.3 视频模板系统
**职责：** 定义字幕样式、位置、动画等

**可用模板：**

| 比例 | 模板 | 说明 |
|------|------|------|
| 9:16 | default | 默认竖屏，白色超粗字幕底部 |
| 9:16 | elegant | 优雅风格，居中+半透明遮罩 |
| 9:16 | minimal | 极简风格，小字幕 |
| 16:9 | default | 默认横屏，适合B站 |
| 16:9 | cinematic | 电影风格，带黑边 |
| 1:1 | card | 卡片风格，适合小红书 |

**使用：**
```python
from video.templates import load_template, list_templates

# 列出模板
print(list_templates())  # {'9:16': ['default', 'elegant', 'minimal'], ...}

# 加载模板
template = load_template('elegant', '9:16')
print(template.subtitle.font_size)  # 72
```

---

### 📄 文档生产层

#### 6. md-to-pdf
**职责：** Markdown → PDF

**特点：**
- 自动调用 illustration-generator
- 中文字体支持
- 纽约客风格排版

**使用：**
```
转换 PDF article.md
```

---

### 📱 发布层

#### 7. wechat-article-formatter
**职责：** Markdown → 微信 HTML

**特点：**
- 自动上传图片
- 微信样式优化
- 可直接粘贴

**使用：**
```
格式化微信文章 article.md
```

#### 8. wechat-publisher-skill
**职责：** 自动发布到微信公众号

---

### ✂️ 视频剪辑层

#### 9. videocut-skills
**职责：** 口播视频自动剪辑

**功能：**
- 🎤 **口误识别**：逐字检测，精准定位
- 🔇 **静音检测**：自动识别 ≥1s 静音片段
- 💬 **语气词处理**：自动识别"嗯""哎"等，精确删除
- 📝 **字幕生成**：Whisper + 词典纠正
- 🔄 **自更新**：从反馈中学习剪辑习惯

**使用：**
```bash
/videocut:剪口播    # 转录 + 口误/静音识别 → 审查稿
/videocut:剪辑      # 执行删除，循环审查直到零口误
/videocut:字幕      # Whisper 转录 → 词典纠正 → 烧录字幕
/videocut:自更新    # 记录反馈，更新规则
```

**技术栈：**
- FunASR（口误识别）
- Whisper large-v3（字幕生成）
- FFmpeg

---

#### 10. filmcut-skills
**职责：** 全自动影视分镜剪辑

**功能：**
- 🎬 **场景检测**：PySceneDetect 识别镜头切换
- 🧠 **智能评分**：构图、运动、人物、美学四维度评分
- 🎵 **节奏同步**：自动对齐音乐节拍点
- 🎨 **蒙太奇规则**：景别渐进、动静匹配、节奏剪辑
- 💻 **纯 CPU 方案**：无需显卡

**镜头评分维度：**
| 维度 | 权重 | 技术 |
|------|------|------|
| 构图质量 | 25% | OpenCV 边缘检测 |
| 运动流畅度 | 20% | 光流法 |
| 人物检测 | 25% | Haar Cascade |
| 美学评分 | 30% | Claude Vision API |

**使用：**
```bash
# 快速剪辑（默认3分钟）
python filmcut.py input.mp4

# 自定义参数
python filmcut.py input.mp4 --duration 180 --min-score 60

# 或在 Claude Code 中
/filmcut:智能剪辑
```

**工作流：**
```
输入视频 → 场景检测 → 镜头分析 → 节奏分析 → 智能剪辑 → 输出成片
```

---

### 🎭 对话生成层

#### 11. persona-dialogue-system
**职责：** 多角色对话模拟（播客/访谈/辩论）

**核心特性：**
- 🎭 **人格化AI角色**：每个角色有独特的缺陷和限制
- 🌊 **状态波动**：时间依赖的情绪/心理变化
- 💔 **创伤约束**：敏感话题触发防御机制
- 🎓 **专业偏见**：领域特定的视角和知识盲区

**三维约束系统：**
| 维度 | 说明 |
|------|------|
| 状态波动 | 基础情绪温度 + 随机抖动 + 触发激活 |
| 创伤约束 | 触发话题 → 防御机制（回避/转移/过激） |
| 专业偏见 | 领域专长 + 思维框架 + 知识盲区 |

**使用：**
```bash
# 初始化项目
python3 scripts/init_project.py my-dialogue-project

# 运行对话（增强版，推荐）
python3 scripts/run_dialogue_enhanced.py my-dialogue-project "什么是进步？" 10
```

**增强功能：**
- 🌊 正弦波状态波动 + 相位偏移
- 🎯 Embedding 语义触发检测
- 💬 智能打断机制
- 🧠 元意识注入（10-15%概率"意识到自己在表演"）

**适用场景：**
- 播客对话生成
- 辩论模拟
- 角色扮演
- 多视角讨论

---

### 🐦 社交媒体层

#### 12. twitter-crawler
**职责：** Twitter 推文爬取 → Markdown

**功能：**
- 爬取指定用户推文
- 支持自定义数量和字段
- 输出 Markdown 和 JSON

**使用：**
```bash
python3 scripts/fetch_tweets.py <用户名> -n 20
```

---

#### 13. twitter-writer
**职责：** Twitter 风格写作

---

## 🔄 完整工作流

### 场景 1：文档 → 抖音视频（最常用）

```
1. 文档解读
   用户: "解读 paper.pdf"
   ↓
   servasyy-document-interpreter
   ↓
   输出: article.md

2. 生成 TTS 脚本
   Claude 自动调用 tts-script-generator
   ↓
   输出: tts_script.json + visual_config.json
   （含智能动画标记）

3. 生成配图（9:16）
   Claude 自动调用 illustration-generator
   ↓
   输出: illustrations/*.png（9:16 竖屏）

4. 生成音频
   python generate_tts_v2.py
   ↓
   输出: audio/*.mp3

5. 合成视频
   python compose_smart.py
   ↓
   输出: 最终视频_9x16.mp4
```

**一句话：** "解读 paper.pdf 并生成抖音视频"

---

### 场景 2：文档 → 微信文章

```
1. 文档解读
   servasyy-document-interpreter
   ↓
   article.md

2. 生成配图
   illustration-generator
   ↓
   illustrations/*.png

3. 格式化微信
   wechat-article-formatter
   ↓
   wechat_article.html

4. 发布
   wechat-publisher-skill
```

---

### 场景 3：文档 → 播客

```
1. 文档解读
   servasyy-document-interpreter
   ↓
   article.md

2. 生成播客脚本
   Claude 改写为对话形式
   ↓
   podcast_script.txt

3. 生成播客
   podcast-generator
   ↓
   podcast.mp3
```

---

### 场景 4：文档 → PDF

```
1. 文档解读
   servasyy-document-interpreter
   ↓
   article.md

2. 生成配图
   illustration-generator
   ↓
   illustrations/*.png

3. 转换 PDF
   md-to-pdf
   ↓
   article.pdf
```

---

## 🎯 关键设计决策

### 1. 为什么默认 9:16？
- 抖音/小红书是主流平台
- 竖屏是移动端主流
- 以后所有任务都用竖屏优先

### 2. 为什么混合 Manim + ASS？
- Manim 生动但慢（~2分钟/段）
- ASS 快速但静态（~10秒/段）
- 混合：3-5段动画 + 其他字幕
- 平衡效果和速度

### 3. 为什么 Claude 智能决策？
- 不需要手动标记
- 自动判断重点片段
- 提高生产效率

### 4. 为什么模块化设计？
- 每个 skill 职责单一
- 可以独立使用
- 也可以组合使用
- 易于维护和扩展

### 5. 为什么共享库？
- 避免代码重复
- 统一接口
- 易于升级

---

## 📊 性能数据

### 文章生成
- 5000字文档 → 8000字文章：~2分钟

### 图像生成
- 24张配图（并行）：~5-10分钟
- 使用缓存：~1分钟

### 视频生成
- 24段视频（全ASS）：~5分钟
- 24段视频（5段Manim + 19段ASS）：~8分钟
- 24段视频（全Manim）：~30分钟

**建议：** 3-5段动画（Claude自动决策）

---

## 🔧 依赖安装

```bash
# Manim（文本动画）
pip install manim

# Edge TTS
pip install edge-tts

# 图像生成
# 已配置多个 provider

# 其他
# - ffmpeg（已安装）
# - 共享模块（已创建）
```

---

## 📝 常用命令速查

### 文章生成
```
解读 paper.pdf
解读并生成微信文章 paper.pdf
解读并生成 PPT paper.pdf
```

### 视频生成
```bash
# 完整流程
python generate_tts_v2.py
python compose_smart.py

# 指定比例
python compose_smart.py --aspect-ratio 16:9

# 指定 TTS 引擎
python generate_tts_v2.py --engine indextts2
```

### 图像生成
```
/illustration-generator article.md
/illustration-generator article.md --workers 8
```

### PDF 生成
```
转换 PDF article.md
```

---

## 🆚 对比其他方案

| 功能 | 其他方案 | 我们的方案 | 优势 |
|------|---------|-----------|------|
| 文章撰写 | 手动 | Qiaomu 风格自动 | ✅ 自动化 |
| 图像生成 | 单一 API | 多 provider | ✅ 稳定性 |
| TTS | Listenhub | 3种引擎 | ✅ 灵活性 |
| 文本动画 | 手动 | Manim 自动 | ✅ 生动性 |
| 视频合成 | 串行 | 并行（4线程） | ✅ 速度 |
| 比例支持 | 16:9 | **默认 9:16** | ✅ 移动优先 |
| 智能决策 | ❌ 手动 | ✅ **Claude 自动** | ✅ 效率 |
| 多平台 | 单一 | 微信/抖音/PDF | ✅ 覆盖面 |

---

## 🐛 故障排除

### 1. 文章生成失败
- 检查文档格式
- 尝试其他格式（PDF → URL）

### 2. 图像生成失败
- 检查 `visual_config.json`
- 查看缓存：`.illustration_cache/`
- 尝试其他 provider

### 3. Manim 失败
- 自动降级为 ASS 字幕
- 检查：`pip install manim`

### 4. TTS 失败
- 检查网络连接
- 尝试其他引擎：`--engine edge-tts`

---

## 📚 重要文档

### 共享库
1. `shared-lib/README.md` - 共享库结构
2. `shared-lib/video/tts/README.md` - TTS 使用说明

### Skills
1. `servasyy-document-interpreter/SKILL.md` - 文章生成
2. `illustration-generator/SKILL.md` - 图像生成
3. `image-to-video/SKILL.md` - 视频生成
4. `image-to-video/TEXT_ANIMATION_README.md` - 动画说明
5. `image-to-video/SMART_VIDEO_WORKFLOW.md` - 视频工作流
6. `podcast-generator/SKILL.md` - 播客生成
7. `md-to-pdf/SKILL.md` - PDF 生成
8. `wechat-article-formatter/SKILL.md` - 微信格式化

---

## 🎯 核心理念

**一句话生产内容：**
```
解读 paper.pdf 并生成抖音视频
```

**Claude 自动：**
1. 解读文档 → Qiaomu 文章
2. 生成 TTS 脚本（含动画标记）
3. 生成 9:16 配图
4. 生成音频
5. 智能合成视频（Manim + ASS）
6. 输出竖屏视频

**以后所有任务都这样！** 🚀

---

## 📊 Skills 依赖关系图

```
文档输入
    ↓
servasyy-document-interpreter（文章生成）
    ↓
    ├─→ tts-script-generator（TTS脚本 + 动画标记）
    │       ↓
    │   illustration-generator（配图生成，9:16）
    │       ↓
    │   image-to-video（视频合成）
    │       ├─→ video.tts（音频生成）
    │       └─→ video.animation（Manim动画）
    │
    ├─→ illustration-generator（配图生成）
    │       ↓
    │   md-to-pdf（PDF生成）
    │
    ├─→ wechat-article-formatter（微信格式化）
    │       ↓
    │   wechat-publisher-skill（微信发布）
    │
    └─→ podcast-generator（播客生成）
            └─→ video.tts（音频生成）
```

---

## 🔄 扩展方向

### 已实现
- ✅ 文章生成（Qiaomu 风格）
- ✅ 图像生成（多 provider）
- ✅ 音频生成（3种 TTS）
- ✅ 视频生成（Manim + ASS）
- ✅ 多平台发布（微信/PDF）
- ✅ 智能决策（Claude 自动）

### 可扩展
- 🔄 更多 TTS 引擎
- 🔄 更多图像风格
- 🔄 更多动画效果
- 🔄 更多发布平台（小红书/B站）
- 🔄 视频转场效果
- 🔄 背景音乐

---

## 📅 更新日志

**2026-01-22：**
- ✅ **文档整理**：补充所有 skill 到 OVERVIEW
  - 新增 videocut-skills（口播剪辑）
  - 新增 filmcut-skills（影视剪辑）
  - 新增 persona-dialogue-system（多角色对话）
  - 新增 twitter-crawler（推文爬取）
  - 新增 twitter-writer（推特写作）

**2026-01-21：**
- ✅ **新增配图风格系统**（shared-lib/illustration/）
  - 风格从 7 种扩展到 **20 种**
  - 新增风格：elegant, minimal, playful, nature, sketch, vintage, scientific, chalkboard, editorial, retro, blueprint, pixel-art, cute
  - 5 种通用布局 + 关键词匹配推荐
- ✅ **新增小红书分支**（illustration-generator --mode xhs）
  - 6 种小红书专用布局（sparse, balanced, dense, list, comparison, flow）
  - XhsGenerator：内容分析、Hook识别、目标受众识别
  - 支持 Swipe Flow 设计（封面→内容→结尾）
- ✅ **新增写作风格系统**（shared-lib/writing/）
  - 5 种写作风格：qiaomu, xiaohongshu, dankoe, wechat, twitter
  - WritingStyleGenerator：风格推荐、风格转换
- ✅ **新增 document-writer skill**
  - 多风格文章撰写
  - 自动风格分析和推荐
- ✅ **新增 PPT 生成系统**（shared-lib/presentation/）
  - 6 种PPT风格 + 5 种布局 + 8 种主题
- ✅ **新增 ppt-generator skill**
- ✅ **新增 comic-generator skill**
  - 9 种漫画风格（classic, ohmsha, dramatic, warm, sepia, vibrant, realistic, wuxia, shoujo）
  - 6 种页面布局（standard, cinematic, dense, splash, mixed, webtoon）
  - 完整工作流：内容分析→角色设计→分镜→生成→PDF

**2026-01-20：**
- ✅ 新增 `manim_composer.py` 模块
- ✅ 实现透明背景 Manim 动画（.mov 格式 + alpha 通道）
- ✅ 手写字幕效果（Write 动画）
- ✅ 背景图叠加（FFmpeg overlay）
- ✅ 字幕样式优化：白色超粗 + 黑色细边框
- ✅ 自动缩放长文本（宽度 85%）
- ✅ 底部定位优化（shift DOWN * 8.8）
- ✅ 创建批量生成脚本 `~/generate_manim_video.py`
- ✅ **新增 BGM 背景音乐支持**
  - 添加 `video/bgm.py` 模块
  - 支持 5 种预设风格（upbeat/epic/emotional/relaxing/corporate）
  - 支持循环播放、淡入淡出、音量控制
  - 动态音频归一化防止过载
- ✅ **新增多尺寸支持**
  - 16:9（横屏，B站/YouTube）
  - 9:16（竖屏，抖音/小红书）
  - 1:1（方形，小红书/Instagram）
- ✅ **新增视频模板系统**
  - 创建 `video/templates.py` 模块
  - 6 种预设模板（default/elegant/minimal/cinematic/card）
  - YAML 格式定义字幕样式、位置、动画
  - 支持自定义模板扩展

**2026-01-19：**
- ✅ 创建共享 video 模块（TTS + 动画）
- ✅ 实现 Manim 文本动画（4种风格）
- ✅ 支持 9:16 竖屏（默认）
- ✅ Claude 智能动画决策
- ✅ 混合方案（Manim + ASS）
- ✅ 自动降级机制
- ✅ 完善多媒体内容生产平台文档

---

## 🔗 快速链接

### 共享库
- `~/.claude/skills/shared-lib/`
- `~/.claude/skills/shared-lib/video/tts/`
- `~/.claude/skills/shared-lib/video/animation/`

### 核心 Skills
- `~/.claude/skills/servasyy-document-interpreter/`
- `~/.claude/skills/illustration-generator/`
- `~/.claude/skills/image-to-video/`
- `~/.claude/skills/podcast-generator/`
- `~/.claude/skills/tts-script-generator/`

### 发布 Skills
- `~/.claude/skills/md-to-pdf/`
- `~/.claude/skills/wechat-article-formatter-skill/`
- `~/.claude/skills/wechat-publisher-skill/`

---

**最后更新：** 2026-01-21  
**系统定位：** 多媒体内容生产平台  
**核心能力：** 文本 + 图像 + 音频 + 视频 + 多平台发布  
**维护者：** Claude + User
