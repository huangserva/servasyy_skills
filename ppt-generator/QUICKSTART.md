# 🚀 PPT 生成系统 - 快速开始指南

## 📖 目录
1. [快速测试](#1-快速测试)
2. [生成完整 PPT（需要图像 API）](#2-生成完整-ppt需要图像-api)
3. [自定义风格](#3-自定义风格)
4. [常见问题](#4-常见问题)

---

## 1. 快速测试

### 1.1 运行测试示例（不生成图片）

```bash
cd ~/.claude/skills/shared-lib
python3 presentation/test_generation.py
```

**可用示例**：
- 示例 1：基础 Prompt 生成
- 示例 2：Session 管理工作流 ⭐ **推荐先看这个**
- 示例 3：风格对比
- 示例 4：自定义风格（EXTEND）
- 示例 5：智能推荐

**运行单个示例**：
```bash
python3 presentation/test_generation.py 2  # 运行示例2
```

### 1.2 查看生成的 Prompts

示例 2 会在 `~/slide-deck/微服务架构设计指南/` 创建真实的目录和 prompt 文件：

```bash
ls ~/slide-deck/微服务架构设计指南/prompts/

# 查看第一个 prompt
cat ~/slide-deck/微服务架构设计指南/prompts/01-slide-封面.md
```

这些 prompt 文件展示了：
- 不同风格的设计指令
- 布局的具体要求
- 颜色、字体、视觉元素定义

---

## 2. 生成完整 PPT（需要图像 API）

### 2.1 准备工作

系统需要图像生成 API 才能真正生成幻灯片图片。你需要集成以下之一：
- DALL-E 3
- Midjourney
- Stable Diffusion
- 其他图像生成 API

### 2.2 完整工作流示例

```python
from presentation import *
import requests  # 或你的图像 API 客户端

# 1. 智能推荐风格
content = "微服务架构设计指南，包括服务拆分、API网关、数据一致性等技术内容"
recs = recommend_styles(content, "微服务架构设计", top_n=3)
print(f"推荐风格: {recs[0]['style']}")

# 2. 创建 Session
session = create_session(
    title="微服务架构设计",
    style=recs[0]['style'],  # 使用推荐的风格
    language='zh',
    audience='experts'
)

# 3. 创建专业目录
output_dir = session.create_output_directory("微服务架构设计")
session.metadata['output_dir'] = str(output_dir)

# 4. 定义幻灯片内容
slides = [
    {'layout': 'cover', 'content': '微服务架构设计指南', 'title': '封面'},
    {'layout': 'section_divider', 'content': '第一章：架构概述', 'title': '章节'},
    {'layout': 'content_left', 'content': '• 服务拆分原则\n• API 网关\n• 数据一致性', 'title': '核心原则'},
]

# 5. 生成幻灯片
gen = PresentationGenerator(session_id=session.session_id)

for i, slide in enumerate(slides, 1):
    # 生成 prompt
    prompt = gen.build_slide_prompt(
        layout=slide['layout'],
        content=slide['content']
    )
    
    # 保存 prompt
    session.add_prompt(i, prompt, save_to_file=True, slide_title=slide['title'])
    
    # 调用图像 API（示例）
    # image_url = your_image_api.generate(prompt)
    # 下载并保存图片
    # with open(output_dir / f'slide_{i:02d}.png', 'wb') as f:
    #     f.write(requests.get(image_url).content)
    
    print(f"✓ 第{i}页: {slide['title']}")

# 6. 导出 PPTX 和 PDF
export_both(output_dir)

print(f"\n✅ 完成！")
print(f"输出目录: {output_dir}")
```

### 2.3 使用现有图片组装 PPT

如果你已经有生成好的图片：

```python
from presentation import export_to_pptx, export_to_pdf
from pathlib import Path

# 确保图片按顺序命名：slide_01.png, slide_02.png, ...
slides_dir = Path('/path/to/your/slides')

# 导出
export_to_pptx(slides_dir, slides_dir / 'presentation.pptx')
export_to_pdf(slides_dir, slides_dir / 'presentation.pdf')
```

---

## 3. 自定义风格

### 3.1 创建企业品牌风格

```python
from presentation import create_custom_style

# 创建模板
create_custom_style('company_brand', extends='apple', location='user')
```

这会创建：`~/.ppt-extensions/styles/company_brand.yaml`

### 3.2 编辑自定义风格

编辑 `~/.ppt-extensions/styles/company_brand.yaml`：

```yaml
name: company_brand
extends: apple
display_name: 公司品牌风格

prompt_template: |
  {base_prompt}  # 继承 apple 的基础风格
  
  [BRAND OVERRIDE]:
  - Brand Color: #FF6B35 (Your Orange)
  - Secondary: #4ECDC4 (Your Teal)
  - Logo: Top right corner, 120x40px
  - Font: Montserrat for headers, Open Sans for body
  - Watermark: "© YourCompany 2024" at bottom
  
  [BRAND RULES]:
  ✅ Use brand colors only
  ✅ Add subtle brand pattern in background
  ❌ No generic colors

best_for:
  - 公司培训
  - 客户演示
  - 销售提案
```

### 3.3 使用自定义风格

```python
gen = PresentationGenerator(style='company_brand')
# 所有生成的 prompt 都会包含你的品牌要求
```

---

## 4. 常见问题

### Q1: 为什么测试示例不生成图片？

**A**: 测试示例只生成 prompt，不调用图像 API。这样你可以：
- 查看不同风格的 prompt 差异
- 测试 Session 管理、目录结构等功能
- 不需要图像 API 也能了解系统

要真正生成图片，需要集成图像 API（见第 2 节）。

### Q2: 生成的 prompts 文件在哪里？

**A**: 
```bash
~/slide-deck/{project-slug}/prompts/
```

示例：
```bash
~/slide-deck/微服务架构设计指南/prompts/01-slide-封面.md
```

### Q3: 如何查看所有可用风格？

```python
from presentation import list_styles

styles = list_styles()
print(f"共 {len(styles)} 种风格:")
for style in sorted(styles):
    print(f"  - {style}")
```

或运行：
```bash
python3 -c "from presentation import list_styles; print('\n'.join(sorted(list_styles())))"
```

### Q4: 如何修改生成的 prompt？

1. 找到 prompt 文件：
   ```bash
   ~/slide-deck/{project}/prompts/01-slide-封面.md
   ```

2. 用文本编辑器打开并修改

3. 使用修改后的 prompt 重新生成图片

### Q5: 推荐算法不准确怎么办？

可以直接指定风格：
```python
gen = PresentationGenerator(
    style='blueprint',  # 直接指定
    language='zh'
)
```

或查看推荐理由：
```python
recs = recommend_styles(content, title, detailed=True)
for r in recs:
    print(f"{r['style']}: {r['reason']}")
```

### Q6: 如何清理测试数据？

```bash
# 删除测试生成的 PPT 目录
rm -rf ~/slide-deck/*

# 删除测试会话
rm -rf ~/.claude/skills/shared-lib/presentation/.sessions/*

# 删除测试的自定义风格
rm -rf ~/.ppt-extensions/
```

---

## 📚 更多资源

- **完整文档**: `~/.claude/skills/ppt-generator/FINAL_REPORT.md`
- **架构设计**: `~/.claude/skills/ppt-generator/INTEGRATION_ARCHITECTURE.md`
- **测试代码**: `~/.claude/skills/shared-lib/presentation/test_*.py`

---

## 🎯 下一步

1. ✅ 运行示例 2，查看生成的 prompt 文件
2. ✅ 尝试不同风格，对比 prompt 差异
3. ✅ 创建自定义风格（如果有品牌需求）
4. 🔧 集成图像生成 API
5. 🚀 开始生成真实的 PPT！

有问题随时问我！🙌
