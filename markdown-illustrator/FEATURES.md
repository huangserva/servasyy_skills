# Markdown Illustrator - 功能完整清单

## ✨ 功能概览

Markdown Illustrator 提供**两大核心功能**，让图片生成变得简单高效。

---

## 🎨 功能1：Markdown文档配图

### 适用场景
- ✅ 已有完整的Markdown文章
- ✅ 需要为多个章节生成配图
- ✅ 希望自动插入图片到文档
- ✅ 需要保持风格一致性

### 核心特性
1. **智能分析** - 自动识别H2章节作为配图点
2. **批量生成** - 一次生成多张配图
3. **自动插入** - 在合适位置插入图片引用
4. **保留原文** - 生成新文件，不修改原始文档

### 使用方式

#### 命令行
```bash
# 基础用法（默认5张纽约客风格）
python3 illustrate.py article.md

# 自定义数量和风格
python3 illustrate.py article.md --style ukiyoe --num 3

# 自定义provider优先级
python3 illustrate.py article.md --priority modelscope,google-local
```

#### 在Claude对话中
```
"帮我给这篇文章配5张纽约客风格的图"
"用markdown-illustrator给我的文档配插图"
"用ModelScope给文章配浮世绘风格的图"
```

### 输出结果
```
原始目录/
├── article.md                    # 原始文件（不修改）
├── article_配图版.md              # 带配图的新文件
└── article_images_newyorker/     # 配图目录
    ├── img_001.jpg
    ├── img_002.jpg
    └── img_003.jpg
```

---

## 🖼️ 功能2：直接提示词生成图片

### 适用场景
- ✅ 只需要单张图片
- ✅ 没有Markdown文档
- ✅ 快速测试效果
- ✅ 生成概念图、封面图

### 核心特性
1. **即时生成** - 提供提示词，立即生成
2. **灵活控制** - 自定义风格、provider、宽高比
3. **独立使用** - 无需其他文件
4. **快速迭代** - 适合测试和调整

### 使用方式

#### 命令行
```bash
# 基础用法
python3 generate_image.py "A golden cat on a book"

# 指定风格
python3 generate_image.py "A warrior" --style newyorker

# 指定provider和输出
python3 generate_image.py "A sunset" --provider modelscope -o sunset.jpg

# 自定义宽高比
python3 generate_image.py "A portrait" --aspect-ratio 9:16
```

#### 在Claude对话中
```
"用markdown-illustrator生成一张图：猫咪坐在书上"
"生成一张纽约客风格的图片：武士在战斗"
"用ModelScope生成：富士山日落"
```

### 输出结果
```
当前目录/
└── generated_20260114_230000.jpg   # 生成的图片
```

---

## 🎭 支持的艺术风格

### 纽约客风格 (newyorker)
- **特点**：黑白钢笔素描 + 朱红色点缀 (#E34234)
- **风格**：极简、编辑插图、知性
- **适用**：商业内容、叙事、评论

**示例：**
```bash
python3 generate_image.py "A business meeting" --style newyorker
```

### 浮世绘风格 (ukiyoe)
- **特点**：鲜艳色彩 + 装饰性线条
- **风格**：日本木版画、扁平透视、东方美学
- **适用**：文化、历史、艺术内容

**示例：**
```bash
python3 generate_image.py "Mount Fuji" --style ukiyoe
```

### 原始模式 (raw)
- **特点**：最小风格修饰
- **风格**：遵循原始提示词
- **适用**：需要精确控制时

**示例：**
```bash
python3 generate_image.py "Photorealistic portrait" --style raw
```

---

## 🔌 支持的图片生成Provider

| Provider | 类型 | 速度 | 质量 | 推荐度 |
|----------|------|------|------|--------|
| **modelscope** | 云端 | 中 (~26秒) | 高 | ⭐⭐⭐⭐⭐ |
| **google-local** | 本地 | 快 (~7秒) | 高 | ⭐⭐⭐⭐ |
| **zimage** | 本地 | 快 (~15秒) | 高 | ⭐⭐⭐⭐ |
| **volcengine** | 云端 | 快 (~10秒) | 高 | ⭐⭐⭐ |
| **apimart** | 云端 | 慢 (~30秒) | 中 | ⭐⭐ |

### 默认优先级
```
modelscope → google-local → zimage → volcengine → apimart
```

### 自定义优先级示例

**只用云端：**
```bash
--priority modelscope,volcengine,apimart
```

**只用本地：**
```bash
--priority google-local,zimage
```

**ModelScope优先：**
```bash
--priority modelscope,google-local
```

---

## 📐 支持的宽高比

| 比例 | 用途 | 示例 |
|------|------|------|
| 16:9 | 横屏、文章插图 | `--aspect-ratio 16:9` |
| 9:16 | 竖屏、手机壁纸 | `--aspect-ratio 9:16` |
| 1:1 | 正方形、社交媒体 | `--aspect-ratio 1:1` |
| 4:3 | 传统照片 | `--aspect-ratio 4:3` |
| 3:4 | 竖向海报 | `--aspect-ratio 3:4` |
| 21:9 | 超宽屏、电影感 | `--aspect-ratio 21:9` |

---

## 🚀 完整工作流示例

### 场景1：写博客配图

```bash
# 步骤1：写好Markdown文章
vim blog_post.md

# 步骤2：快速生成测试图，确定风格
python3 generate_image.py "Blog concept" --style newyorker -o test.jpg
python3 generate_image.py "Blog concept" --style ukiyoe -o test2.jpg

# 步骤3：选择纽约客风格，批量配图
python3 illustrate.py blog_post.md --style newyorker --num 5

# 步骤4：生成封面图
python3 generate_image.py "Blog cover art" \
    --style newyorker \
    --aspect-ratio 16:9 \
    -o cover.jpg

# 完成！
```

### 场景2：技术文档配图

```bash
# 步骤1：为技术文档配图（浮世绘风格更有视觉冲击）
python3 illustrate.py tech_doc.md --style ukiyoe --num 3

# 步骤2：额外生成架构图（使用原始模式）
python3 generate_image.py "System architecture diagram" \
    --style raw \
    -o architecture.jpg
```

### 场景3：社交媒体配图

```bash
# 生成正方形配图（适合Instagram等）
python3 generate_image.py "Inspirational quote visual" \
    --style newyorker \
    --aspect-ratio 1:1 \
    -o social.jpg
```

---

## 💡 使用技巧

### 提示词技巧

**✅ 好的提示词：**
- 具体、清晰、有细节
- 包含主体、背景、氛围
- 使用英文（效果最好）

```
"A golden retriever puppy playing with a red ball in a sunny park"
"A minimalist zen garden with raked sand, soft morning light"
"A samurai standing under cherry blossoms at sunset"
```

**❌ 避免的提示词：**
- 太模糊："A picture"
- 太复杂：包含过多元素
- 直接中文：应翻译为英文

### Provider选择技巧

**场景1：速度优先**
```bash
--priority google-local,zimage  # 本地服务最快
```

**场景2：稳定性优先**
```bash
--priority modelscope,volcengine  # 云端稳定
```

**场景3：质量优先**
```bash
--priority google-local,modelscope,zimage  # 高质量provider
```

### 批量生成技巧

**方式1：循环生成**
```bash
for i in {1..5}; do
    python3 generate_image.py "Concept ${i}" -o "concept_${i}.jpg"
done
```

**方式2：文档配图（推荐）**
```bash
# 自动为所有章节配图
python3 illustrate.py document.md --num auto
```

---

## 🔧 高级配置

### 自定义配置文件

编辑 `config.yaml`:

```yaml
default_style: newyorker
default_num_images: 5
default_priority:
  - modelscope
  - google-local
  - zimage
```

### Python API集成

```python
# 文档配图
from illustrate import MarkdownIllustrator

illustrator = MarkdownIllustrator(
    style='newyorker',
    custom_priority=['modelscope', 'google-local']
)

report = illustrator.illustrate('article.md', num_images=5)

# 直接生成
from generate_image import generate_image_from_prompt

image_path = generate_image_from_prompt(
    prompt="A golden cat",
    style='newyorker',
    output_path='cat.jpg'
)
```

---

## 📊 性能对比

### 单张图片生成

| Provider | 耗时 | 适用场景 |
|----------|------|----------|
| google-local | 7秒 | 快速测试 |
| modelscope | 26秒 | 稳定方案 ⭐ |
| zimage | 15秒 | 本地高质 |
| volcengine | 10秒 | 快速云端 |

### 5张图片批量生成

| Provider | 总耗时 | 平均耗时 |
|----------|--------|----------|
| google-local | ~35秒 | ~7秒/张 |
| modelscope | ~130秒 | ~26秒/张 |
| zimage | ~75秒 | ~15秒/张 |

---

## ❓ 常见问题

### Q: 两个功能怎么选择？

**A:** 
- 有Markdown文档 → 用 `illustrate.py`
- 只要单张图片 → 用 `generate_image.py`
- 先测试后批量 → 先用 `generate_image.py`，再用 `illustrate.py`

### Q: 提示词必须是英文吗？

**A:** 
建议英文，效果最好。中文提示词建议先翻译为英文。

### Q: 如何选择风格？

**A:**
- 商业、叙事内容 → newyorker
- 文化、历史内容 → ukiyoe  
- 需要精确控制 → raw

### Q: Provider都失败怎么办？

**A:**
1. 检查网络连接
2. 确认至少一个provider可用
3. 查看错误信息调整
4. 尝试不同的provider

---

## 📚 相关资源

- **README.md** - 详细使用文档
- **INSTALL.md** - 安装指南
- **skill.md** - Skill描述
- **skill.prompt** - Claude行为指南

---

**Markdown Illustrator - 让配图变得简单！** 🎨
