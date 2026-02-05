---
name: illustration-generator
description: 统一配图技能，支持文章配图、封面生成、小红书图片系列、单图修改/添加/删除、3变体风格预览。20种风格×多种布局。
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite
---

# Illustration Generator（统一配图技能）

一个 skill 解决所有配图需求。

## ⚠️ 重要：自动化工作流程

当用户要求为文章生成配图时，你必须按以下步骤执行：

### Step 1: 分析文章结构
```bash
python3 ~/.claude/skills/illustration-generator/scripts/generate.py article.md --preview
```
这会分析文章并推荐风格，但不会生成图片。

### Step 2: 读取并填写 visual_config.json
分析完成后，读取生成的 `visual_config.json` 文件。对于每个 `visual_description` 为空的章节，你需要：

1. 阅读该章节的 `content_summary`
2. 根据章节内容，生成一段**具体的视觉场景描述**（50-150字）
3. 描述应包含：场景、主体、动作、氛围、色调等具体视觉元素

**示例：**
- 章节内容："AI如何改变工作流程"
- visual_description: "一个现代化办公室场景，中央是一个发光的AI机器人助手，周围环绕着多个悬浮的工作流程图标（日历、邮件、文档），蓝紫色科技光芒从机器人向四周扩散，背景是半透明的数据流"

### Step 3: 更新配置文件
使用 Edit 工具更新 `visual_config.json`，填入所有 visual_description。

### Step 4: 生成图片
```bash
python3 ~/.claude/skills/illustration-generator/scripts/generate.py article.md --style <chosen_style>
```

### 快速示例
```bash
# 1. 预览分析
python3 ~/.claude/skills/illustration-generator/scripts/generate.py article.md --preview

# 2. 读取配置，手动填写 visual_description（你来完成）
# 3. 生成图片
python3 ~/.claude/skills/illustration-generator/scripts/generate.py article.md --style tech
```

---

## 功能

- 🔍 **自动分析**：分析 Markdown 文章，识别需要配图的位置
- 🎨 **3变体预览**：推荐 3 种风格变体供选择
- ⚡ **并行生成**：多线程生成 + MD5 缓存
- 🔄 **单图修改**：重新生成某张配图
- ➕ **添加配图**：在指定位置添加新图
- 🗑️ **删除配图**：移除不需要的图片
- 📖 **封面生成**：单独生成封面图
- 📱 **小红书模式**：生成 1-10 张信息图系列

## 使用方式

### 1. 文章配图（完整流程）

```bash
/illustration-generator article.md
```

### 2. 指定风格

```bash
/illustration-generator article.md --style tech
```

### 3. 只生成封面

```bash
/illustration-generator article.md --cover-only
```

### 4. 单图修改

```bash
/illustration-generator article.md --regenerate illustration_03.png
```

### 5. 添加/删除配图

```bash
/illustration-generator article.md --add "在第二章后添加流程图"
/illustration-generator article.md --remove illustration_05.png
```

### 6. 小红书模式（新增）

```bash
# 小红书图片系列
/illustration-generator content.md --mode xhs

# 指定风格和图片数量
/illustration-generator content.md --mode xhs --style cute --count 5

# 指定布局
/illustration-generator content.md --mode xhs --style notion --layout dense
```

## 20 种风格

| 分类 | 风格 | 说明 |
|------|------|------|
| 经典 | newyorker | 纽约客杂志，极简线条 |
| 经典 | ukiyoe | 日本浮世绘，东方美学 |
| 科技 | tech | 科技数码，深色+霓虹 |
| 科技 | blueprint | 技术蓝图，工程制图 |
| 科技 | pixel-art | 像素艺术，8-bit 游戏 |
| 极简 | notion | 极简手绘，知识分享 |
| 极简 | minimal | 极简禅意，大量留白 |
| 极简 | flat | 扁平插画，商业通用 |
| 温暖 | warm | 温暖亲切，柔和色调 |
| 温暖 | playful | 活泼可爱，趣味入门 |
| 温暖 | cute | 可爱甜美，小红书风 |
| 艺术 | watercolor | 水彩画风，艺术感 |
| 艺术 | sketch | 手绘草稿，创意想法 |
| 复古 | vintage | 复古做旧，怀旧美学 |
| 复古 | retro | 80s霓虹，潮流文化 |
| 专业 | elegant | 精致优雅，商务专业 |
| 专业 | scientific | 学术科学，论文图表 |
| 专业 | editorial | 杂志编辑，信息图表 |
| 教育 | chalkboard | 黑板粉笔，教育培训 |
| 自然 | nature | 自然有机，环保健康 |

## 5 种通用布局

| 布局 | 说明 | 使用场景 |
|------|------|---------|
| single | 单一场景 | 封面、普通配图 |
| infographic | 信息图 | 多要点、特点列表 |
| comparison | 对比图 | 左右对比、优缺点 |
| flow | 流程图 | 步骤、时间线 |
| scene | 场景图 | 叙事、人物故事 |

## 小红书专用布局

| 布局 | 密度 | 使用场景 |
|------|------|---------|
| sparse | 1-2点 | 封面、金句引言 |
| balanced | 3-4点 | 常规内容页 |
| dense | 5-8点 | 知识卡片、干货 |
| list | 4-7项 | 清单、排名、步骤 |
| comparison | 2侧 | 优缺点、A vs B |
| flow | 3-6步 | 流程、时间线 |

## 小红书工作流

```
用户输入内容
      ↓
┌─────────────────────────┐
│ Step 1: 内容分析         │
│ - 识别内容类型          │
│ - 推荐风格+布局         │
│ - 识别Hook类型          │
│ - 估算图片数量          │
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│ Step 2: 3变体预览        │
│ 1. cute - 可爱甜美       │
│ 2. notion - 知识卡片     │
│ 3. warm - 温暖生活       │
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│ Step 3: 生成大纲         │
│ - 封面（sparse）         │
│ - 内容页（balanced/dense）│
│ - 结尾（sparse + CTA）   │
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│ Step 4: 批量生成         │
│ - 竖版 3:4 比例         │
│ - 手绘插画风格          │
│ - 信息图排版            │
└─────────────────────────┘
```

## 内容类型映射

| 内容类型 | 推荐风格 | 推荐布局 |
|---------|---------|---------|
| 种草安利 | cute | balanced |
| 干货分享 | notion | dense |
| 测评对比 | tech | comparison |
| 教程步骤 | playful | flow |
| 避坑指南 | bold | list |
| 清单合集 | minimal | list |
| 个人故事 | warm | balanced |

## Hook 类型

| 类型 | 示例 |
|------|------|
| 数字钩子 | "5个方法"、"3分钟学会"、"99%的人不知道" |
| 痛点钩子 | "踩过的坑"、"后悔没早知道"、"别再..." |
| 好奇钩子 | "原来..."、"竟然..."、"没想到..." |
| 利益钩子 | "省钱"、"变美"、"效率翻倍" |
| 身份钩子 | "打工人必看"、"学生党"、"新手妈妈" |

## 调用 shared-lib

```python
from illustration import (
    # 通用配图
    IllustrationGenerator,
    recommend_styles,
    analyze_article,
    
    # 小红书专用
    XhsGenerator,
    analyze_xhs_content,
    generate_xhs_outline,
    recommend_xhs_styles
)

# 小红书内容分析
analysis = analyze_xhs_content("5个AI工具推荐")
print(analysis['content_type'])  # 干货分享
print(analysis['recommended_style'])  # notion

# 生成大纲
outline = generate_xhs_outline(content, style="notion", image_count=5)

# 推荐风格
styles = recommend_xhs_styles("美妆护肤分享")
```

## 输出

### 文章配图
```
article_dir/
├── article.md
├── visual_config.json
└── images/illustrations/
    ├── cover.png
    ├── illustration_01.png
    └── ...
```

### 小红书图片
```
xhs-images/{topic}/
├── analysis.md           # 内容分析
├── outline.md            # 图片大纲
├── 01-cover-{slug}.png   # 封面
├── 02-content-{slug}.png # 内容页
├── ...
└── 05-ending-{slug}.png  # 结尾
```
