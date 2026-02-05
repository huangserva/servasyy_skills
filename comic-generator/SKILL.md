---
name: comic-generator
description: 知识漫画生成器，支持多种风格（Ligne Claire/漫画教程风/武侠风等）。将文章/教程/人物传记转换为漫画形式。
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite
---

# Comic Generator（知识漫画生成器）

将知识内容转换为漫画形式，支持多种风格和布局。

## 功能

- 📚 **内容分析**：自动分析内容类型、推荐风格
- 🎭 **角色生成**：根据内容自动生成角色设计
- 📖 **分镜设计**：智能分页、分镜布局
- 🎨 **多风格支持**：9种预设风格
- 📐 **多布局支持**：6种页面布局
- 🔄 **单页修改**：支持重新生成、添加、删除页面

## 使用方式

```bash
# 基础用法
/comic-generator article.md

# 指定风格
/comic-generator article.md --style ohmsha

# 指定布局
/comic-generator article.md --style classic --layout cinematic

# 指定比例
/comic-generator article.md --aspect 4:3
```

## 9 种漫画风格

| 风格 | 说明 | 适用内容 |
|------|------|---------|
| classic | Ligne Claire 传统欧漫 | 人物传记、历史 |
| ohmsha | 日式教程漫画（哆啦A梦风） | 技术教程、科普 |
| dramatic | 戏剧性高对比 | 冲突、转折点 |
| warm | 温暖柔和 | 个人故事、成长 |
| sepia | 复古棕褐色调 | 历史、回忆 |
| vibrant | 鲜艳活泼 | 儿童内容、趣味科普 |
| realistic | 写实风格 | 商业、专业内容 |
| wuxia | 武侠水墨风 | 武侠、中国历史 |
| shoujo | 少女漫画风 | 情感、校园 |

## 6 种页面布局

| 布局 | 分镜数 | 说明 |
|------|-------|------|
| standard | 4-6 | 标准网格，通用 |
| cinematic | 3-4 | 电影感宽幅 |
| dense | 6-9 | 密集信息 |
| splash | 1-2 | 全页大图 |
| mixed | 3-6 | 混合大小 |
| webtoon | 3-5 | 竖向滚动 |

## 3 种比例

| 比例 | 说明 |
|------|------|
| 3:4 | 竖版（默认） |
| 4:3 | 横版 |
| 16:9 | 宽屏 |

## 自动选择逻辑

| 内容信号 | 推荐风格 | 推荐布局 |
|---------|---------|---------|
| 教程、入门、指南 | ohmsha | webtoon |
| 编程、AI、技术 | ohmsha | dense |
| 历史、古代 | sepia | cinematic |
| 个人故事、成长 | warm | standard |
| 冲突、突破 | dramatic | splash |
| 武侠、仙侠 | wuxia | splash |
| 情感、校园 | shoujo | standard |
| 传记 | classic | mixed |

## 工作流程

### Step 1: 内容分析

```
用户输入内容
      ↓
┌─────────────────────────┐
│ 分析内容                 │
│ - 目标受众              │
│ - 核心主题              │
│ - 关键人物              │
│ - 推荐页数（5-25页）     │
│ - 推荐风格+布局         │
└─────────────────────────┘
      ↓
输出: analysis.md
```

### Step 2: 角色设计

```
┌─────────────────────────┐
│ 生成角色                 │
│ - 主角设计              │
│ - 配角设计              │
│ - 视觉规范              │
│ - 角色关系图            │
└─────────────────────────┘
      ↓
输出: characters/
      ├── characters.md
      └── characters.png
```

### Step 3: 分镜设计

```
┌─────────────────────────┐
│ 生成分镜                 │
│ - 封面设计              │
│ - 每页分镜              │
│ - 对话/旁白             │
│ - 视觉提示              │
└─────────────────────────┘
      ↓
输出: storyboard.md
```

### Step 4: 用户确认

提供 3 种变体供选择：
- A: 时间线叙事 + 推荐风格
- B: 主题叙事 + 备选风格
- C: 角色叙事 + 备选风格

### Step 5: 生成图片

```
┌─────────────────────────┐
│ 批量生成                 │
│ - 保存 prompt           │
│ - 调用图像 API          │
│ - 保持角色一致性         │
└─────────────────────────┘
      ↓
输出: 00-cover.png, 01-page.png, ...
```

### Step 6: 合并 PDF

```bash
# 自动合并所有页面为 PDF
```

## 输出结构

```
comic/{topic-slug}/
├── source.md              # 源内容
├── analysis.md            # 内容分析
├── characters/
│   ├── characters.md      # 角色规范
│   └── characters.png     # 角色参考图
├── storyboard.md          # 分镜脚本
├── prompts/
│   ├── 00-cover.md
│   └── NN-page-{slug}.md
├── 00-cover.png           # 封面
├── 01-page-{slug}.png     # 内容页
├── ...
└── {topic-slug}.pdf       # 最终 PDF
```

## 页面修改

### 重新生成单页

```bash
/comic-generator regenerate comic/turing-story/ --page 03
```

### 添加新页

```bash
/comic-generator add comic/turing-story/ --after 03 --content "新增内容描述"
```

### 删除页面

```bash
/comic-generator delete comic/turing-story/ --page 05
```

## 调用 shared-lib

```python
import sys
sys.path.insert(0, str(Path.home() / '.claude' / 'skills' / 'shared-lib'))

from illustration import IllustrationGenerator

gen = IllustrationGenerator()
# 使用 comic 专用风格生成
```

## Ohmsha 风格特别说明

使用 `--style ohmsha` 时：

**默认使用哆啦A梦角色：**
- 大雄（Nobita）：学习者角色
- 哆啦A梦（Doraemon）：导师角色，用道具解释概念
- 胖虎（Gian）：挑战/障碍角色
- 静香（Shizuka）：提问/澄清角色

**要求：**
- 必须使用视觉隐喻（道具、动作场景）
- 禁止"说话头像"式的静态对话
- 页面标题要有叙事性

## 与 baoyu-comic 的区别

| 特性 | baoyu-comic | comic-generator |
|------|------------|-----------------|
| 风格数量 | 9种 | 9种（相同） |
| 布局数量 | 6种 | 6种（相同） |
| 共享库 | 独立 | 使用 shared-lib |
| PDF 合并 | TypeScript | Python |
| 扩展性 | EXTEND.md | YAML 配置 |

## 参考资源

- `references/styles/` - 风格定义
- `references/layouts/` - 布局定义
- `references/storyboard-template.md` - 分镜模板
- `references/character-template.md` - 角色模板
