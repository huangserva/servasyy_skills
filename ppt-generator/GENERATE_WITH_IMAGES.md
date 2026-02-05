# 🎨 使用图像 API 生成 NotebookLM PPT

## 📖 方案说明

你的系统已经有完整的图像生成能力！

### ✅ 已有组件
1. **图像 API**: `~/.claude/skills/shared-lib/image_api.py`
2. **配置文件**: `~/.claude/skills/servasyy-document-interpreter/config.yaml`
3. **PPT 系统**: 已完成的 presentation 模块

---

## 🚀 两种生成方式

### 方式 1：仅生成 Prompts（已完成）✅

```bash
cd ~/.claude/skills/shared-lib
python3 presentation/generate_notebooklm.py
```

**输出**：
- `~/slide-deck/notebooklm-功能介绍/prompts/*.md`（7 个 prompt 文件）
- 不生成图片，只保存生成指令

**用途**：
- 查看不同风格的 prompt 差异
- 手动编辑和优化 prompts
- 快速测试，不消耗 API

---

### 方式 2：完整生成（Prompts + 图片）🎨

```bash
cd ~/.claude/skills/shared-lib
python3 presentation/generate_notebooklm_full.py
```

**这个脚本会**：
1. ✅ 生成 7 个 prompt 文件
2. ✅ 调用 `image_api.py` 生成 7 张幻灯片图片
3. ✅ 自动导出 PPTX 和 PDF

**预计时间**：
- 每张图片：10-30 秒
- 总时间：2-5 分钟（7 张图片）

**输出**：
```
~/slide-deck/notebooklm-功能介绍/
├── prompts/
│   ├── 01-slide-封面.md
│   ├── 02-slide-什么是-notebooklm.md
│   └── ...
├── slide_01.png          ← 生成的图片
├── slide_02.png
├── ...
├── presentation.pptx     ← 自动导出的 PPTX
└── presentation.pdf      ← 自动导出的 PDF
```

---

## 🔧 image_api.py 支持的服务

根据你的 `image_api.py`，支持以下图像生成服务：

### 1. **z-image**（本地 ComfyUI）
- 优先级最高
- 如果本地运行 ComfyUI，会自动使用

### 2. **volcengine**（doubao-4）
- 字节跳动火山引擎
- 需要配置 API key

### 3. **apimart**（nano-banana-pro）
- 备选方案

### **auto 模式**（推荐）
```python
generate_image(prompt, output_path, provider='auto')
```

会自动按优先级尝试：
1. z-image
2. volcengine
3. apimart

---

## 📝 配置检查

### 查看当前配置
```bash
cat ~/.claude/skills/servasyy-document-interpreter/config.yaml
```

### 典型配置示例
```yaml
# 默认配置
defaults:
  image_model: 'z-image'

# z-image 配置（本地 ComfyUI）
zimage:
  base_url: 'http://219.147.109.250:8198/mw/api/v1'
  api_key: 'your-api-key'
  default_workflow: 'z_image_turbo'

# volcengine 配置
volcengine:
  api_key: 'your-doubao-api-key'
  
# apimart 配置
apimart:
  api_key: 'your-apimart-key'
```

---

## 🎯 快速开始

### 步骤 1：检查配置（可选）

```bash
# 查看配置
cat ~/.claude/skills/servasyy-document-interpreter/config.yaml

# 如果没有 API key，可以先用方式 1 生成 prompts
```

### 步骤 2A：仅生成 Prompts（推荐先测试）

```bash
cd ~/.claude/skills/shared-lib
python3 presentation/generate_notebooklm.py
```

查看生成的 prompts：
```bash
ls -lh ~/slide-deck/notebooklm-功能介绍/prompts/
cat ~/slide-deck/notebooklm-功能介绍/prompts/01-slide-封面.md
```

### 步骤 2B：完整生成（包含图片）

```bash
cd ~/.claude/skills/shared-lib
python3 presentation/generate_notebooklm_full.py
```

会提示：
```
⚠️  注意：此脚本会调用图像生成 API
是否继续？(y/n):
```

输入 `y` 开始生成。

---

## 💡 常见问题

### Q1: 图片生成失败怎么办？

**A**: 检查以下几点：
1. config.yaml 是否有有效的 API key
2. 网络连接是否正常
3. 查看错误信息，可能是 API 额度或限流

### Q2: 可以手动生成单张图片吗？

**A**: 可以！
```python
from image_api import generate_image

# 使用已生成的 prompt
with open('~/slide-deck/notebooklm-功能介绍/prompts/01-slide-封面.md', 'r') as f:
    prompt = f.read()

generate_image(
    prompt=prompt,
    output_path='~/slide-deck/notebooklm-功能介绍/slide_01.png',
    width=1920,
    height=1080,
    provider='auto'
)
```

### Q3: 如何更换图像生成服务？

**A**: 修改 provider 参数：
```python
generate_image(..., provider='volcengine')  # 指定使用火山引擎
generate_image(..., provider='auto')        # 自动选择
```

### Q4: 生成的图片不满意怎么办？

**A**: 
1. 编辑对应的 prompt 文件
2. 重新生成该图片
3. 或者尝试不同的风格

---

## 🎨 尝试不同风格

### 使用 notion 风格（SaaS 仪表盘风格）

修改 `generate_notebooklm_full.py` 的风格选择：

```python
# 不使用推荐，直接指定风格
session = create_session(
    title="NotebookLM 功能介绍",
    style='notion',      # 改为 notion
    language='zh',
    audience='general'
)
```

### 或使用 blueprint（技术蓝图风格）

```python
session = create_session(
    title="NotebookLM 功能介绍",
    style='blueprint',   # 改为 blueprint
    language='zh',
    audience='experts'
)
```

---

## 📚 下一步

1. ✅ **先运行方式 1**：生成 prompts，查看效果
2. ✅ **检查 config.yaml**：确认有可用的 API
3. ✅ **运行方式 2**：完整生成 PPT
4. ✅ **查看结果**：`open ~/slide-deck/notebooklm-功能介绍/`

---

## 🎊 你现在可以

- **A. 直接运行完整生成**（如果 config 已配置）
- **B. 先查看已生成的 prompts**（已经有了）
- **C. 手动编辑 prompts 后再生成图片**
- **D. 尝试不同风格重新生成**

告诉我你想怎么做！
