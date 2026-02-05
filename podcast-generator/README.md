# 📻 Podcast Generator Skill

从Markdown文档一键生成访谈式播客（MP3）

## 🎯 功能

⚠️ **重要说明：**
访谈式播客需要精心设计的对话脚本才能达到最佳效果。本skill生成模板脚本，**需要人工编写访谈对话**。

✅ **推荐工作流程：**
```
Markdown文档 
    ↓
【自动】提取文本 + 生成模板
    ↓
【人工】编写访谈对话（关键步骤！）⭐
    ↓
【自动】TTS合成 + 合并音频
    ↓
高质量访谈播客MP3
```

✅ **核心特性：**
- 双人访谈模式（晓伊女声 + 云扬男声）
- 自然停顿（0.5秒对话间隔）
- 优化段落（50字左右/段）
- 高质量语音（微软Azure Neural TTS）
- **人工编写脚本**（确保访谈质量）

---

## 📦 安装依赖

```bash
# 1. 安装 edge-tts
python3 -m pip install edge-tts --break-system-packages

# 2. 安装 ffmpeg
brew install ffmpeg  # macOS
# 或 sudo apt install ffmpeg  # Linux
```

---

## 🚀 快速开始

### 方式1：命令行使用

```bash
# 基础用法
python3 ~/.claude/skills/podcast-generator/skill.py 文档.md

# 指定输出文件
python3 ~/.claude/skills/podcast-generator/skill.py 文档.md \
  --output 我的播客.mp3

# 自定义参数
python3 ~/.claude/skills/podcast-generator/skill.py 文档.md \
  --output 播客.mp3 \
  --title "楚汉争霸" \
  --female-voice zh-CN-XiaoxiaoNeural \
  --pause 0.8
```

### 方式2：Python代码调用

```python
from skill import PodcastGenerator

# 创建生成器
generator = PodcastGenerator()

# 自定义参数（可选）
generator.female_voice = 'zh-CN-XiaoyiNeural'  # 晓伊
generator.male_voice = 'zh-CN-YunyangNeural'   # 云扬
generator.pause_duration = 0.5  # 停顿0.5秒

# 生成播客
output_file = generator.generate_podcast(
    md_file='楚汉争霸.md',
    output_file='楚汉争霸播客.mp3',
    title='楚汉争霸'
)

print(f"播客已生成: {output_file}")
```

---

## 📝 使用流程

### 完整流程

```
1. 准备Markdown文档
   └─> 楚汉争霸.md

2. 运行命令
   └─> python3 skill.py 楚汉争霸.md

3. 自动执行6个步骤：
   ├─> 步骤1: 提取纯文本
   ├─> 步骤2: AI改写为访谈脚本
   ├─> 步骤3: 解析脚本
   ├─> 步骤4: 生成音频片段
   ├─> 步骤5: 生成静音间隔
   └─> 步骤6: 合并音频

4. 得到播客MP3
   └─> 楚汉争霸_播客.mp3
```

### 中间文件

生成过程中会保存这些文件（在 `workspace/` 目录）：

```
workspace/
├── 楚汉争霸_纯文本.txt       - 提取的纯文本
├── 楚汉争霸_访谈脚本.txt     - AI生成的访谈脚本
└── 临时音频文件（自动清理）
```

---

## ⚙️ 参数说明

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `markdown` | Markdown文件路径 | 必填 |
| `--output`, `-o` | 输出MP3文件路径 | 与输入同名 |
| `--title` | 播客标题 | 文件名 |
| `--female-voice` | 女声ID | zh-CN-XiaoyiNeural |
| `--male-voice` | 男声ID | zh-CN-YunyangNeural |
| `--pause` | 对话间停顿（秒） | 0.5 |

### 可用声音列表

**女声：**
- `zh-CN-XiaoyiNeural` - 晓伊（活泼，推荐）⭐
- `zh-CN-XiaoxiaoNeural` - 晓晓（温柔自然）
- `zh-CN-XiaohanNeural` - 晓涵（严肃）
- `zh-CN-XiaomengNeural` - 晓梦（可爱）

**男声：**
- `zh-CN-YunyangNeural` - 云扬（专业沉稳，推荐）⭐
- `zh-CN-YunxiNeural` - 云希（年轻阳光）
- `zh-CN-YunjianNeural` - 云健（激情运动）

查看所有声音：
```bash
edge-tts --list-voices | grep zh-CN
```

---

## 💡 最佳实践

### 1. Markdown文档要求

✅ **推荐格式：**
```markdown
# 主标题

## 章节1

段落内容...

## 章节2

段落内容...
```

❌ **避免：**
- 过多图片链接
- 复杂嵌套结构
- 代码块过多

### 2. 优化脚本质量

生成后的访谈脚本保存在 `workspace/XXX_访谈脚本.txt`，你可以：

1. **手动优化脚本**（推荐）
   ```bash
   # 1. 生成初始脚本
   python3 skill.py 文档.md
   
   # 2. 编辑脚本
   vim workspace/文档_访谈脚本.txt
   
   # 3. 使用优化后的脚本重新生成
   python3 ../../scripts/generate_interview_podcast.py \
     --script workspace/文档_访谈脚本.txt \
     --output 最终播客.mp3
   ```

2. **脚本编写技巧：**
   - 每段约50字
   - 晓晓负责提问和惊叹
   - 云扬负责讲解和回答
   - 避免过于频繁切换

### 3. 停顿时间选择

- **0.3秒** - 快节奏，信息密集
- **0.5秒** - 推荐，自然舒适 ⭐
- **0.8秒** - 慢节奏，更从容

---

## 📊 性能参考

| 文档大小 | 对话轮次 | 生成时间 | 文件大小 |
|----------|----------|----------|----------|
| 5KB | ~20轮 | ~1分钟 | ~0.5MB |
| 20KB | ~80轮 | ~4分钟 | ~2.5MB |
| 50KB | ~150轮 | ~7分钟 | ~5MB |

*时间不包含脚本人工优化*

---

## 🔧 故障排除

### 问题1：edge-tts找不到

```bash
python3 -m pip install edge-tts --break-system-packages
```

### 问题2：ffmpeg找不到

```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### 问题3：生成的脚本质量不好

当前版本使用基础模板，建议：
1. 生成初始脚本
2. 手动编辑优化
3. 使用 `generate_interview_podcast.py` 重新生成

### 问题4：声音不自然

尝试：
- 调整停顿时间：`--pause 0.8`
- 更换声音：`--female-voice zh-CN-XiaoxiaoNeural`
- 手动优化脚本，控制段落长度

---

## 🎓 示例

### 示例1：基础使用

```bash
python3 skill.py 楚汉争霸.md
```

输出：
```
📖 步骤1: 提取纯文本...
   ✅ 提取完成，字数: 3521

🤖 步骤2: AI改写为访谈脚本...
   ✅ 脚本生成完成，对话轮次: 89

📝 步骤3: 解析脚本...
   ✅ 解析完成，共89轮对话

🎤 步骤4: 生成89个音频片段...
   [1/89] 晓晓: 欢迎来到《历史不装》，我是晓晓...
   ...
   
✅ 播客生成成功！
📁 文件: 楚汉争霸_播客.mp3
📊 大小: 2.6 MB
```

### 示例2：自定义声音

```bash
python3 skill.py 科技前沿.md \
  --output 科技播客.mp3 \
  --female-voice zh-CN-XiaoxiaoNeural \
  --male-voice zh-CN-YunxiNeural \
  --pause 0.3
```

---

## 📚 相关工具

- **访谈脚本生成工具：** `scripts/generate_interview_podcast.py`
- **完整文档：** `scripts/README_PODCAST.md`

---

## 🔄 版本历史

- **v1.0.0** (2026-01-14)
  - ✅ 初始版本
  - ✅ 完整6步流程自动化
  - ✅ 基础脚本模板
  - ✅ 支持自定义声音和停顿

---

## 📧 反馈

如有问题或建议，请联系开发者。

---

**Enjoy! 🎙️**
