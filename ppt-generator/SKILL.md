---
name: ppt-generator
description: 生成专业 PPT 演示文稿，支持 22 种风格，自动根据内容选择最佳风格，输出到 ~/ppt-output/
---

# PPT Generator Skill

专注于 PPT 生成的完整解决方案。

## 触发条件

当用户请求涉及以下内容时激活：
- 生成 PPT / 幻灯片 / 演示文稿
- 制作 PPT / 做 PPT
- 大纲转 PPT
- PPT 风格选择
- 修改 PPT 某一页

---

## 风格选择指南（22 种风格）

当用户提出 PPT 需求时，**你（Claude）根据以下指南选择风格**，不要调用任何 Python 推荐函数。

### 分析维度

1. **场景**: tech / business / education / creative / lifestyle / academic / gaming / historical
2. **受众**: beginners / general / experts / executives / children
3. **调性**: formal / casual / playful / serious / warm / professional

### 风格评分表

#### 第一梯队：通用高质量风格（质量分 9-10）

| 风格 | 质量 | 稳定 | 适用场景 | 适用受众 | 调性 |
|------|------|------|----------|----------|------|
| **apple** | 10 | 9 | tech(10), business(9), education(7), data(9) | executives(10), general(9), experts(8) | professional, elegant |
| **minimal** | 9 | 9 | business(10), tech(8) | executives(10), experts(8) | formal, zen |
| **corporate** | 9 | 9 | business(10), data(8) | executives(9), general(8) | formal, trustworthy |

#### 第二梯队：专业领域风格（质量分 8）

| 风格 | 质量 | 稳定 | 适用场景 | 适用受众 | 调性 |
|------|------|------|----------|----------|------|
| **blueprint** | 8 | 9 | tech(10), data(9), academic(8) | experts(10), general(7) | technical, precise |
| **notion** | 8 | 9 | tech(9), business(8), data(10) | general(9), experts(8) | clean, functional |
| **scientific** | 8 | 8 | academic(10), tech(7) | experts(10), academics(10) | formal, precise |
| **editorial** | 8 | 8 | business(8), academic(7) | general(8), experts(7) | professional, readable |
| **editorial_infographic** | 8 | 8 | academic(9), tech(8), education(7) | general(9), experts(8) | informative, clear |
| **intuition_machine** | 8 | 7 | tech(9), academic(9) | experts(9), bilingual(10) | technical, bilingual |

#### 第三梯队：教育风格（质量分 7-8）

| 风格 | 质量 | 稳定 | 适用场景 | 适用受众 | 调性 |
|------|------|------|----------|----------|------|
| **sketch_notes** | 8 | 7 | education(10), tech(6) | beginners(10), general(8) | warm, friendly |
| **chalkboard** | 7 | 8 | education(10) | beginners(9), children(8) | nostalgic, teaching |
| **fantasy_animation** | 8 | 7 | education(8), creative(9), story(10) | children(10), beginners(9) | playful, magical |

#### 第四梯队：创意风格（质量分 7-8）

| 风格 | 质量 | 稳定 | 适用场景 | 适用受众 | 调性 |
|------|------|------|----------|----------|------|
| **watercolor** | 8 | 7 | lifestyle(10), creative(9), health(8), historical(8) | general(9), beginners(8) | warm, artistic |
| **vector_illustration** | 8 | 7 | education(8), creative(9) | children(9), beginners(8) | cute, friendly |
| **dark_atmospheric** | 8 | 7 | gaming(10), creative(9), entertainment(10) | general(8), youth(9) | dramatic, cinematic |
| **bold_editorial** | 8 | 7 | business(8), marketing(10) | general(9), executives(7) | bold, impactful |
| **storytelling** | 7 | 7 | story(10), creative(8) | general(8), beginners(7) | narrative, emotional |

#### 第五梯队：特色风格（质量分 6-7）

| 风格 | 质量 | 稳定 | 适用场景 | 适用受众 | 调性 |
|------|------|------|----------|----------|------|
| **pixel_art** | 7 | 7 | gaming(10), tech(6) | youth(10), developers(8) | retro, playful |
| **vintage** | 7 | 7 | historical(10), story(8) | general(8) | nostalgic, classic |
| **neumorphism** | 6 | 6 | tech(7), creative(7) | general(7) | modern, soft |
| **material** | 7 | 8 | tech(8), business(6) | general(8) | clean, systematic |
| **fluent** | 7 | 8 | tech(8), business(7) | general(8) | modern, fluid |

---

## 快速选择指南

### 按场景选择

| 用户说的内容包含 | 推荐风格（按优先级） |
|-----------------|---------------------|
| AI、技术、系统、架构、数据 | apple → blueprint → notion |
| 商业、投资、企业、汇报、提案 | corporate → apple → minimal |
| 教程、学习、入门、培训 | sketch_notes → chalkboard → apple |
| 儿童、故事、动画、有趣 | fantasy_animation → vector_illustration |
| 游戏、像素、复古、开发者 | pixel_art → dark_atmospheric |
| **历史、传统、文化、古代、探险、怀旧** | **vintage → watercolor → editorial** |
| 生活、健康、旅行、艺术 | watercolor → vector_illustration |
| 科学、学术、研究、论文 | scientific → blueprint → editorial_infographic |
| 产品发布、营销、发布会 | bold_editorial → dark_atmospheric → apple |
| SaaS、产品、仪表盘、指标 | notion → apple → minimal |

### 按受众选择

| 受众类型 | 推荐风格 | 原因 |
|---------|---------|------|
| 高管/投资人 | minimal, corporate, apple | 简洁、专业、高端 |
| 技术专家 | blueprint, scientific, intuition_machine | 精确、信息密集 |
| 初学者/入门 | sketch_notes, chalkboard, fantasy_animation | 友好、易懂 |
| 儿童 | fantasy_animation, vector_illustration, pixel_art | 有趣、可爱 |
| 普通大众 | apple, notion, watercolor | 平衡、通用 |

### 按调性选择

| 调性 | 推荐风格 |
|------|---------|
| 正式专业 | corporate, minimal, apple |
| 温暖友好 | sketch_notes, watercolor, fantasy_animation |
| 活泼有趣 | pixel_art, vector_illustration, chalkboard |
| 高端大气 | minimal, dark_atmospheric, bold_editorial |
| 技术精确 | blueprint, scientific, notion |

---

## 主题色选择（仅 apple 风格）

| 主题 | 适用场景 |
|------|---------|
| soft_blue | 科技、AI、数据（默认） |
| deep_indigo | 商业、金融、专业 |
| fresh_green | 健康、环保、成长 |
| warm_orange | 教育、活力、创意 |
| rose_pink | 生活方式、时尚 |
| elegant_purple | 创意、高端、神秘 |
| cool_teal | 清新、现代 |
| neutral_grey | 极简、中性 |

---

## 可用布局

| 布局 | 用途 |
|------|------|
| cover | 封面页 |
| section_divider | 章节分隔页 |
| content_left | 左对齐内容页 |
| content_center | 居中强调页 |
| content_two_column | 两栏对比页 |
| title_hero | 大标题英雄页 |
| key_stat | 关键数据页 |
| quote_callout | 引用强调页 |
| icon_grid | 图标网格页 |
| three_columns | 三栏布局页 |
| timeline | 时间线/流程页 |
| comparison | 对比页 |
| hub_spoke | 中心辐射页 |
| pyramid | 金字塔层级页 |
| agenda | 议程/目录页 |

---

## 工作流

### 流程 1：生成 PPT

1. **分析用户需求** - 识别场景、受众、调性
2. **选择风格** - 根据上述评分表选择最合适的风格
3. **告知用户** - 说明选择的风格和原因
4. **创建输出目录** - `~/ppt-output/{项目名}/`
5. **生成幻灯片** - 调用 Python 执行层

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / '.claude/skills/shared-lib'))

from presentation import create_session, PresentationGenerator

# 1. 创建 session
session = create_session(
    title='项目标题',
    style='vintage',  # 你选择的风格
    language='zh',
    audience='general'
)

# 2. 创建输出目录
output_dir = session.create_output_directory('项目标题')

# 3. 生成幻灯片
gen = PresentationGenerator(style='vintage')
gen.generate_slide(
    layout='cover',
    content='标题\n副标题',
    output_path=str(output_dir / 'slide_01.png')
)
```

### 流程 2：批量生成

```python
# 批量生成多页
results = gen.batch_generate_slides(
    slides_config=[
        {'layout': 'cover', 'content': '标题'},
        {'layout': 'content_left', 'content': '要点列表'},
    ],
    output_dir=str(output_dir)
)
```

### 流程 3：导出 PPTX

```bash
python ~/.claude/skills/ppt-generator/scripts/assemble_pptx.py \
    --input_dir ~/ppt-output/项目名/ \
    --output ~/ppt-output/项目名/presentation.pptx
```

---

## 输出目录结构

```
~/ppt-output/{项目名}/
├── prompts/
│   ├── 01-slide-封面.md
│   ├── 02-slide-xxx.md
│   └── ...
├── slide_01.png
├── slide_02.png
├── slide_03.png
├── ppt_content.yaml
├── presentation.pptx
└── presentation.pdf
```

---

## 配置依赖

图片生成依赖 `~/.claude/skills/shared-lib/config.yaml`，包含：

| Provider | 说明 |
|----------|------|
| google-local | 本地 Google API 代理（优先） |
| ModelScope | 阿里通义 Z-Image |
| volcengine | 字节跳动火山引擎 |
| ApiMart | ApiMart 图像生成 |

---

## 注意事项

1. **风格选择由 AI 完成** - 根据本文档的评分表判断，不调用 Python 推荐函数
2. **质量优先** - 多个风格匹配度接近时，选择质量分更高的
3. **受众优先** - 儿童/初学者 → 友好风格；高管 → 简洁风格
4. **稳定性考虑** - 重要场合选择稳定性高的风格（apple, corporate, minimal）
5. **风格一致** - 一个 PPT 只用一种风格，不要混用
