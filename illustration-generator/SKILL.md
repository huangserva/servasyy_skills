---
name: illustration-generator
description: 统一配图技能，支持文章配图、封面生成、小红书图片系列、单图修改/添加/删除、3变体风格预览。现已扩充至 40 种精选风格（集成 Vibeshot 视觉图谱）× 多种布局。
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

## 13 大领域风格图谱（Style Atlas · 46 种精选落地风格）

系统全面吸收 **Vibeshot 风格图谱体系**，覆盖 13 大艺术与设计顶级领域，提供完整的材质、构图、光影及 Prompt 规范：

| 领域分类 | 谱系子类 | 风格标识 (`--style`) | 核心视觉特征 / 艺术语言 |
|---------|---------|---------------------|----------------------|
| **01 西方艺术史与绘画** | 古典至浪漫主义 | `baroque` | 巴洛克油画，剧烈明暗对比与史诗光影 |
| **01 西方艺术史与绘画** | 矫饰主义 | `mannerism` | 优雅拉长人体，文艺复兴晚期冷调 |
| **01 西方艺术史与绘画** | 极简艺术主义 | `minimal` | 极简留白，哲学本质纯粹美感 |
| **01 西方艺术史与绘画** | 经典古典优雅 | `elegant` | 高端艺术，精致优雅商务 |
| **02 东方与全球传统** | 中国壁画与宗教绘画 | `dunhuang` | 敦煌莫高窟壁画，矿物颜料天女流线 |
| **02 东方与全球传统** | 中国笔墨与绘画技法 | `blue-green-landscape` | 传统青绿山水，千里江山孔雀石绿 |
| **02 东方与全球传统** | 日本传统视觉 | `ukiyoe` | 江户浮世绘，经典木版画意境 |
| **03 插画、出版与概念设计** | 拼贴与印刷插画 | `risograph` | Riso孔版套色印刷，吸墨网点荧光色 |
| **03 插画、出版与概念设计** | 手绘媒介 | `gouache` | 不透明水粉绘本，平刷笔触哑光质感 |
| **03 插画、出版与概念设计** | 编辑与文学插画 | `newyorker` | 纽约客极简钢笔线条，人文幽默讽刺 |
| **03 插画、出版与概念设计** | 手绘媒介 | `watercolor` | 通透诗意水彩，自然晕染与光影 |
| **03 插画、出版与概念设计** | 手绘媒介 | `sketch` | 手绘铅笔草稿速写，头脑风暴构思 |
| **03 插画、出版与概念设计** | 编辑与文学插画 | `editorial` | 严肃编辑排版，深度新闻调查 |
| **03 插画、出版与概念设计** | 手绘与情感插画 | `warm` | 温暖治愈手绘，生活故事与成长 |
| **04 漫画、动漫与角色** | 动漫造型与上色 | `anime` | 当代精细日漫厚涂，透亮眼神发丝 |
| **04 漫画、动漫与角色** | 动漫造型与上色 | `cel-shading` | 经典赛璐璐动漫画风，干净硬边阴影 |
| **04 漫画、动漫与角色** | 角色造型与可爱风 | `cute` | 甜美可爱，小红书穿搭生活 |
| **05 平面、海报与排版** | 装饰图形 | `art-deco-graphic` | 装饰艺术平面，爵士阶梯几何金边 |
| **05 平面、海报与排版** | 亚文化与反设计 | `psychedelic-poster` | 60s迷幻摇滚海报，酸性扭曲旋涡 |
| **05 平面、海报与排版** | 现代主义平面 | `flat` | 现代商业扁平，通用企业报告流程 |
| **05 平面、海报与排版** | 实验字体与文字编排 | `chalkboard` | 黑板粉笔板书，课堂教学培训 |
| **06 摄影、光学与胶片** | 胶片与曝光 | `film-35mm` | 35mm银盐真胶片摄影，自然颗粒感 |
| **06 摄影、光学与胶片** | 光学表现与长曝光 | `long-exposure` | 慢门长曝光摄影，车流流光丝滑水面 |
| **07 电影、电视与视频** | 镜头、色彩与后期语言 | `three-strip-technicolor` | 三条片特艺彩色，好莱坞高浓郁胶片 |
| **07 电影、电视与视频** | 戏剧、歌舞与浪漫影像 | `hollywood-musical` | 好莱坞黄金歌舞，盛大华丽聚光灯 |
| **07 电影、电视与视频** | 时代影像与胶片记忆 | `vintage` | 复古做旧与泛黄质感，时代传记回忆 |
| **07 电影、电视与视频** | 复古视效与蒸汽波 | `retro` | 80s复古蒸汽波，霓虹与潮流娱乐 |
| **08 CG、3D、数字与游戏** | 风格化几何 | `low-poly` | 低多边形几何面，清爽极简3D棱角 |
| **08 CG、3D、数字与游戏** | 风格化几何 | `voxel-art` | 体素艺术，3D微缩立方体网格 |
| **08 CG、3D、数字与游戏** | 复古游戏与像素 | `pixel-art` | 8-bit复古像素艺术，游戏开发者 |
| **08 CG、3D、数字与游戏** | 三维渲染与科技视觉 | `tech` | 科技数码，深色调配霓虹光效 |
| **08 CG、3D、数字与游戏** | 程序工程制图 | `blueprint` | 工程蓝图图纸，精确架构与结构 |
| **08 CG、3D、数字与游戏** | 科学可视化图表 | `scientific` | 严谨学术科学，论文文献图表 |
| **09 动画与动态设计** | 木偶与黏土定格 | `clay-stop-motion` | 黏土定格动画，手工物理质感指纹 |
| **09 动画与动态设计** | 传统逐帧动画 | `cel-animation` | 吉卜力手绘逐帧，呼吸感治愈动势 |
| **09 动画与动态设计** | 动态图形与趣味动画 | `playful` | 活泼趣味动效，轻松入门小白教学 |
| **10 UI、UX与界面** | 当代界面视觉 | `liquid-glass-ui` | 流体玻璃界面，毛玻璃折射与流体态 |
| **10 UI、UX与界面** | 当代界面视觉 | `claymorphic-ui` | 黏土拟态UI，轻软圆润3D界面卡片 |
| **10 UI、UX与界面** | 界面系统与极简卡片 | `notion` | Notion极简手绘，知识框架卡片 |
| **11 流行文化、亚文化与网络** | 朋克未来想象 | `cyberpunk` | 赛博朋克，密集雨夜霓虹与高科技 |
| **11 流行文化、亚文化与网络** | 生态与多元未来想象 | `solarpunk` | 太阳朋克，生态共生与玻璃太阳能 |
| **11 流行文化、亚文化与网络** | 生态与自然美学 | `nature` | 绿色自然有机，环保与健康生活 |
| **12 建筑、空间与环境** | 复兴、工艺与装饰建筑 | `art-nouveau-architecture` | 新艺术运动建筑，高迪流线自然铁艺 |
| **12 建筑、空间与环境** | 后现代、解构与参数建筑 | `postmodern-architecture` | 后现代主义建筑，孟菲斯古典拼贴 |
| **13 材质、表面与产品** | 首饰与精密装饰工艺 | `cloisonne-enamel` | 掐丝珐琅景泰蓝，细金丝与宝石釉料 |
| **13 材质、表面与产品** | 工业设计与产品造型 | `playful-rounded-product` | 圆润趣味工业造型，温润哑光触感 |

### 领域查询指令
```bash
# 查看全部 13 大领域
python3 ~/.claude/skills/illustration-generator/scripts/generate.py --domains

# 查看某个领域下的所有风格（支持编号或名称）
python3 ~/.claude/skills/illustration-generator/scripts/generate.py --domain 09
python3 ~/.claude/skills/illustration-generator/scripts/generate.py --domain 动画
```

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
