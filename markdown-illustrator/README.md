# Markdown Illustrator

为Markdown文档自动生成配图的智能工具

## 功能特点

✨ **智能分析** - 自动识别文章结构和章节  
🎨 **多种风格** - 支持纽约客、浮世绘等艺术风格  
🔄 **灵活路由** - 支持多个图片生成API，可自定义优先级  
📸 **自动插入** - 在合适位置插入配图  
💪 **容错机制** - 支持自动降级和重试  

## 快速开始

### 基础用法

```bash
# 为文章配图（默认5张纽约客风格）
python3 illustrate.py my_article.md

# 指定配图风格和数量
python3 illustrate.py my_article.md --style ukiyoe --num 3

# 自定义provider优先级（ModelScope优先）
python3 illustrate.py my_article.md --priority modelscope,google-local,zimage
```

### Python API

```python
from illustrate import MarkdownIllustrator

# 创建配图工具
illustrator = MarkdownIllustrator(
    style='newyorker',
    provider='auto',
    custom_priority=['modelscope', 'google-local']
)

# 执行配图
report = illustrator.illustrate('my_article.md', num_images=5)

print(f"成功生成 {report['success']} 张配图")
print(f"配图版文档: {report['output_md']}")
```

## 支持的风格

### 纽约客风格 (newyorker)
- 黑白钢笔线条
- 朱红色点缀 (#E34234)
- 极简艺术
- 适合：叙事、人文、商业内容

### 浮世绘风格 (ukiyoe)
- 鲜艳饱和色彩
- 装饰性线条
- 东方美学
- 适合：历史、文化、艺术内容

## 支持的图片生成Provider

| Provider | 类型 | 速度 | 质量 | 说明 |
|----------|------|------|------|------|
| google-local | 本地 | 快 (~7秒) | 高 | Gemini API |
| modelscope | 云端 | 中 (~26秒) | 高 | 通义万相 |
| zimage | 本地 | 快 (~15秒) | 高 | ComfyUI |
| volcengine | 云端 | 快 (~10秒) | 高 | 火山引擎 |
| apimart | 云端 | 慢 (~30秒) | 中 | ApiMart |

### 默认优先级
```
google-local → modelscope → zimage → volcengine → apimart
```

### 自定义优先级示例

```bash
# ModelScope优先
python3 illustrate.py article.md --priority modelscope,google-local

# 只用云端服务
python3 illustrate.py article.md --priority modelscope,volcengine,apimart

# 只用本地服务
python3 illustrate.py article.md --priority google-local,zimage
```

## 命令行参数

```
positional arguments:
  markdown_file         Markdown文件路径

optional arguments:
  -h, --help            帮助信息
  --style, -s          配图风格 (newyorker|ukiyoe)
  --num, -n            配图数量 (默认: 自动)
  --priority, -p       自定义provider优先级
  --output-dir, -o     图片输出目录
```

## 输出文件

```
原始目录/
├── my_article.md                    # 原始文件（不修改）
├── my_article_配图版.md              # 带配图的新文件
└── my_article_images_newyorker/     # 配图目录
    ├── img_001.jpg
    ├── img_002.jpg
    └── img_003.jpg
```

## 使用示例

### 示例1：博客文章配图

```bash
python3 illustrate.py blog_post.md \
    --style newyorker \
    --num 5 \
    --priority modelscope,google-local
```

### 示例2：技术文档配图

```bash
python3 illustrate.py technical_doc.md \
    --style ukiyoe \
    --num 3 \
    --priority google-local
```

### 示例3：在代码中使用

```python
from illustrate import MarkdownIllustrator

# 为多篇文章批量配图
articles = ['article1.md', 'article2.md', 'article3.md']

illustrator = MarkdownIllustrator(
    style='newyorker',
    custom_priority=['modelscope', 'google-local']
)

for article in articles:
    print(f"处理: {article}")
    report = illustrator.illustrate(article, num_images=5)
    print(f"完成: {report['success']}/{report['total']}")
```

## 配置要求

### 必需
- Python 3.8+
- `shared-lib/image_api.py`
- 至少一个可用的图片生成provider

### 可选
- PIL/Pillow (用于图片处理)
- 各provider的API密钥或本地服务

## 注意事项

1. **生成时间**：取决于provider和图片数量，通常每张7-30秒
2. **API限制**：注意各provider的配额和限制
3. **自动降级**：如果首选provider失败，会自动尝试下一个
4. **图片质量**：不同provider生成的图片质量和风格可能略有差异

## 故障排除

### 问题：所有provider都失败

**解决方案**：
1. 检查网络连接
2. 确认API key是否有效
3. 检查本地服务是否运行
4. 查看错误日志确定具体原因

### 问题：生成速度慢

**解决方案**：
1. 使用本地provider (google-local, zimage)
2. 减少配图数量
3. 使用自定义优先级，优先选择快速provider

### 问题：图片风格不符合预期

**解决方案**：
1. 尝试不同的style选项
2. 检查visual_strategy是否准确
3. 可以在代码中自定义prompt

## 进阶用法

### 自定义视觉策略

```python
class CustomIllustrator(MarkdownIllustrator):
    def generate_visual_strategies(self, sections, num_images=None):
        # 自定义视觉描述生成逻辑
        strategies = []
        for section in sections[:num_images]:
            # 调用LLM生成更智能的描述
            visual_strategy = self.generate_with_llm(section)
            strategies.append((section, visual_strategy, section))
        return strategies
```

## License

MIT

## 贡献

欢迎提交Issue和Pull Request！

---

## 功能2：直接提示词生成图片

### 快速开始

```bash
# 基础用法
python3 generate_image.py "A golden cat sitting on a book"

# 指定纽约客风格
python3 generate_image.py "A warrior in battle" --style newyorker

# 指定浮世绘风格  
python3 generate_image.py "Mount Fuji at sunset" --style ukiyoe

# 使用ModelScope provider
python3 generate_image.py "A modern city skyline" --provider modelscope

# 自定义输出文件名
python3 generate_image.py "A beautiful landscape" -o landscape.jpg

# 竖屏格式（9:16）
python3 generate_image.py "A portrait" --aspect-ratio 9:16
```

### Python API

```python
from generate_image import generate_image_from_prompt

# 生成图片
output_path = generate_image_from_prompt(
    prompt="A golden cat on a book",
    style='newyorker',
    provider='auto',
    custom_priority=['modelscope', 'google-local'],
    output_path='cat.jpg',
    aspect_ratio='16:9'
)

print(f"图片已保存到: {output_path}")
```

### 命令行参数

```
必需参数:
  prompt                提示词（英文）

可选参数:
  --style, -s          图片风格 (newyorker|ukiyoe|raw)
  --provider, -p       指定provider (auto|modelscope|google-local|...)
  --priority           自定义优先级 (逗号分隔)
  --output, -o         输出文件路径
  --aspect-ratio, -a   宽高比 (16:9|9:16|1:1|4:3|3:4|21:9)
```

### 风格说明

| 风格 | 描述 | 适用场景 |
|------|------|----------|
| newyorker | 黑白钢笔素描 + 朱红色点缀 | 编辑插图、商业内容 |
| ukiyoe | 日本浮世绘风格，鲜艳色彩 | 文化、历史、艺术内容 |
| raw | 原始提示词，最小风格修饰 | 需要精确控制时 |

### 使用示例

#### 示例1：快速生成

```bash
python3 generate_image.py "A peaceful zen garden"
```

输出：
```
✅ 生成成功！
💾 图片已保存
文件: generated_20260114_230000.jpg
大小: 256.3 KB
Provider: modelscope
```

#### 示例2：指定风格和provider

```bash
python3 generate_image.py "A samurai under cherry blossoms" \
    --style ukiyoe \
    --provider modelscope \
    -o samurai.jpg
```

#### 示例3：自定义优先级

```bash
# 优先本地服务，云端备用
python3 generate_image.py "A sunset over ocean" \
    --priority google-local,zimage,modelscope
```

#### 示例4：不同宽高比

```bash
# 横屏 16:9
python3 generate_image.py "A landscape" --aspect-ratio 16:9

# 竖屏 9:16（手机壁纸）
python3 generate_image.py "A portrait" --aspect-ratio 9:16

# 正方形 1:1（社交媒体）
python3 generate_image.py "A product photo" --aspect-ratio 1:1

# 超宽屏 21:9（影院）
python3 generate_image.py "A cinematic scene" --aspect-ratio 21:9
```

### 提示词技巧

#### 好的提示词

✅ 具体、清晰、有细节
```
"A golden retriever puppy playing with a red ball in a sunny park"
```

✅ 包含构图、光线、氛围
```
"A minimalist zen garden with raked sand patterns, soft morning light, peaceful atmosphere"
```

✅ 英文描述（效果最好）
```
"A modern city skyline at sunset with purple and orange clouds"
```

#### 避免的提示词

❌ 太模糊
```
"A picture"  # 太笼统
```

❌ 太复杂
```
"A cat and a dog and a bird and a fish all playing together in a forest with mountains and rivers..."  # 太多元素
```

❌ 中文直译
```
"一个猫"  # 应该翻译为 "A cat"
```

### 在Claude对话中使用

```
User: 帮我生成一张图片：金色的猫坐在书上

Droid: 我来生成这张图片。

[将中文翻译为英文]
Prompt: "A golden cat sitting on a book"

[执行命令]
python3 generate_image.py "A golden cat sitting on a book" --style newyorker

[显示结果]
✅ 图片已生成！文件：generated_20260114_230000.jpg
```

### 提示词翻译示例

| 中文 | 英文 |
|------|------|
| 一只金色的猫坐在书上 | A golden cat sitting on a book |
| 富士山日落 | Mount Fuji at sunset |
| 现代都市天际线 | A modern city skyline |
| 武士在樱花树下 | A samurai under cherry blossom trees |
| 宁静的禅宗花园 | A peaceful zen garden |
| 星空夜景 | A starry night sky |

### 组合使用两个功能

你可以先生成单张图片测试效果，满意后再批量为文档配图：

```bash
# 1. 先测试单张
python3 generate_image.py "A warrior concept" --style newyorker -o test.jpg

# 2. 查看效果，满意后批量生成
python3 illustrate.py article.md --style newyorker --num 5
```

### 性能对比

| Provider | 单张耗时 | 5张耗时 | 推荐场景 |
|----------|----------|---------|----------|
| google-local | ~7秒 | ~35秒 | 本地快速测试 |
| modelscope | ~26秒 | ~130秒 | 云端稳定方案 ⭐ |
| zimage | ~15秒 | ~75秒 | 本地高质量 |

### 故障排除

**问题：提示词是中文**
```bash
# ❌ 错误
python3 generate_image.py "一只猫"

# ✅ 正确
python3 generate_image.py "A cat"
```

**问题：生成失败**
```
解决方案：
1. 检查网络连接
2. 尝试其他provider：--provider modelscope
3. 使用自定义优先级：--priority modelscope,volcengine
```

**问题：风格不符合预期**
```
解决方案：
1. 尝试不同风格：--style ukiyoe
2. 使用raw模式精确控制：--style raw
3. 在提示词中加入风格描述
```

---

## 两个功能对比

| 特性 | Markdown配图 | 直接生成图片 |
|------|-------------|-------------|
| 输入 | Markdown文件 | 提示词 |
| 输出 | 多张图片+配图版MD | 单张图片 |
| 数量 | 1-N张 | 1张 |
| 自动化 | 高（自动分析章节） | 低（手动指定） |
| 适用场景 | 文档插图 | 快速单图生成 |
| 使用难度 | 简单 | 更简单 |

### 选择建议

**使用Markdown配图（illustrate.py）当：**
- ✅ 有完整的Markdown文档
- ✅ 需要为多个章节配图
- ✅ 希望自动插入图片到文档
- ✅ 希望保持风格一致性

**使用直接生成（generate_image.py）当：**
- ✅ 只需要单张图片
- ✅ 没有Markdown文档
- ✅ 快速测试效果
- ✅ 生成概念图、测试图

---

## 完整工作流示例

### 场景：创建一篇配图博客

```bash
# 步骤1：先生成几张测试图，确定风格
python3 generate_image.py "Tech concept 1" --style newyorker -o test1.jpg
python3 generate_image.py "Tech concept 2" --style ukiyoe -o test2.jpg

# 步骤2：决定使用纽约客风格

# 步骤3：为完整文档配图
python3 illustrate.py blog_post.md --style newyorker --num 5

# 步骤4：如果需要额外的封面图
python3 generate_image.py "Blog cover illustration" \
    --style newyorker \
    --aspect-ratio 16:9 \
    -o cover.jpg
```

完成！现在你有：
- ✅ 5张文章插图（自动插入到Markdown）
- ✅ 1张封面图
- ✅ 配图版Markdown文档
- ✅ 原始图片文件夹

