# 访谈式播客一键生成工具

## 🎙️ 简介

将文本内容自动转换为双人访谈式播客（MP3）。

**特点：**
- ✅ 双人对话（晓晓女声 + 云扬男声）
- ✅ 自然停顿（0.5秒对话间隔）
- ✅ 优化段落（50字左右/段）
- ✅ 高质量语音（微软Azure Neural TTS）
- ✅ 一键生成

---

## 📦 依赖安装

```bash
# 1. 安装 edge-tts
python3 -m pip install edge-tts --break-system-packages

# 2. 安装 ffmpeg（macOS）
brew install ffmpeg
```

---

## 🚀 快速开始

### 方式1：从访谈脚本生成

**1. 准备脚本文件**（格式：`晓晓：xxx` 和 `云扬：xxx`）

```
【访谈式播客】楚汉争霸

晓晓：欢迎来到《历史不装》，我是晓晓。今天咱们聊聊楚汉争霸。
云扬：好的。很多人觉得刘邦就是人多欺负人少，其实完全不对。
晓晓：那到底是怎么回事呢？
云扬：这场战争其实是17打1。你得把彭越、英布、陈平、张良、萧何、韩信全算上。
```

**2. 生成播客**

```bash
python3 scripts/generate_interview_podcast.py \
  --script 访谈脚本.txt \
  --output 播客.mp3
```

### 方式2：从Markdown生成（半自动）

```bash
# 第一步：生成初步脚本
python3 scripts/generate_interview_podcast.py \
  --markdown 文档.md \
  --output 播客.mp3

# 会生成: 播客_script.txt（供你修改）

# 第二步：修改脚本后重新生成
python3 scripts/generate_interview_podcast.py \
  --script 播客_script.txt \
  --output 播客_最终版.mp3
```

---

## ⚙️ 参数说明

### 基础参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--script` | 访谈脚本文件 | - |
| `--markdown` | Markdown文档 | - |
| `--output`, `-o` | 输出MP3文件 | **必填** |

### 高级参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--pause` | 对话间停顿（秒） | 0.5 |
| `--segment-length` | 每段目标字数 | 50 |
| `--female-voice` | 女声ID | zh-CN-XiaoxiaoNeural |
| `--male-voice` | 男声ID | zh-CN-YunyangNeural |
| `--female-rate` | 女声语速 | +5% |
| `--male-rate` | 男声语速 | +3% |

---

## 📝 脚本格式要求

访谈脚本必须遵循以下格式：

```
晓晓：对话内容（50字左右）
云扬：对话内容（50字左右）
晓晓：对话内容
云扬：对话内容
```

**注意：**
- 必须使用中文冒号 `：`
- 只支持 `晓晓` 和 `云扬` 两个角色
- 建议每段50字左右，最长不超过80字
- 避免过于频繁切换（影响节奏）

---

## 🎤 可用声音列表

### 中文女声
- `zh-CN-XiaoxiaoNeural` - **晓晓**（推荐，温柔自然）
- `zh-CN-XiaoyiNeural` - 晓伊（活泼）
- `zh-CN-XiaohanNeural` - 晓涵（严肃）
- `zh-CN-XiaomengNeural` - 晓梦（可爱）

### 中文男声
- `zh-CN-YunyangNeural` - **云扬**（推荐，专业沉稳）
- `zh-CN-YunxiNeural` - 云希（年轻）
- `zh-CN-YunjianNeural` - 云健（激情）

### 查看所有声音

```bash
edge-tts --list-voices | grep zh-CN
```

---

## 💡 使用示例

### 示例1：基础使用

```bash
python3 scripts/generate_interview_podcast.py \
  --script 楚汉争霸_访谈脚本.txt \
  --output 楚汉争霸播客.mp3
```

### 示例2：自定义停顿

```bash
# 更短停顿（0.3秒）- 更紧凑
python3 scripts/generate_interview_podcast.py \
  --script 脚本.txt \
  --output 播客.mp3 \
  --pause 0.3

# 更长停顿（0.8秒）- 更从容
python3 scripts/generate_interview_podcast.py \
  --script 脚本.txt \
  --output 播客.mp3 \
  --pause 0.8
```

### 示例3：自定义声音

```bash
# 使用晓伊（活泼女声）+ 云希（年轻男声）
python3 scripts/generate_interview_podcast.py \
  --script 脚本.txt \
  --output 播客.mp3 \
  --female-voice zh-CN-XiaoyiNeural \
  --male-voice zh-CN-YunxiNeural
```

### 示例4：调整语速

```bash
# 女声更快，男声正常
python3 scripts/generate_interview_podcast.py \
  --script 脚本.txt \
  --output 播客.mp3 \
  --female-rate +10% \
  --male-rate +0%
```

---

## 🔧 故障排除

### 问题1：edge-tts命令找不到

```bash
# 解决方法
python3 -m pip install edge-tts --break-system-packages
```

### 问题2：ffmpeg命令找不到

```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### 问题3：生成失败

检查脚本格式：
- 确保使用中文冒号 `：`
- 确保只有晓晓和云扬两个角色
- 确保每段对话有内容

### 问题4：声音不自然

尝试调整参数：
- 增加停顿时间：`--pause 0.8`
- 增加段落长度：`--segment-length 70`
- 调整语速：`--female-rate +3%`

---

## 📊 性能参考

| 对话轮次 | 生成时间 | 文件大小 |
|----------|----------|----------|
| 10轮 | ~30秒 | ~0.5 MB |
| 50轮 | ~2分钟 | ~2 MB |
| 100轮 | ~4分钟 | ~4 MB |

---

## 🎯 最佳实践

### 1. 脚本编写建议

✅ **好的对话：**
```
晓晓：项羽火烧咸阳后分了18个诸侯王，听起来挺霸气的。
云扬：霸气是霸气，但分得太随意了。刘邦功劳最大，你猜分到哪儿？巴蜀！
```

❌ **不好的对话：**
```
晓晓：哦
云扬：对
晓晓：然后呢？
```
（太短，太频繁）

### 2. 段落长度控制

- **推荐：50字左右**
- 最短：20字
- 最长：80字
- 每3-5轮可以有1-2个长段落（80字）

### 3. 停顿时间选择

- **0.3秒** - 快节奏，信息密集
- **0.5秒** - 推荐，自然舒适
- **0.8秒** - 慢节奏，更从容

---

## 📚 脚本模板

### 模板1：历史故事

```
【访谈式播客】标题

晓晓：欢迎来到《历史不装》，我是晓晓。
云扬：我是云扬。
晓晓：今天咱们聊聊XXX。很多人觉得XXX，你怎么看？
云扬：这个说法其实不对。真实情况是XXX。
晓晓：哦！那具体是怎么回事呢？
云扬：要从XXX说起。当时XXX。

[正文对话...]

晓晓：今天的故事就到这里。
云扬：感谢收听，我们下期再见。
晓晓：拜拜～
```

### 模板2：知识科普

```
【访谈式播客】标题

晓晓：大家好，我是晓晓。今天我们来聊聊XXX这个话题。
云扬：我是云扬。这个话题确实很有意思。
晓晓：云扬你能先给大家科普一下XXX吗？
云扬：好的。简单来说，XXX是指XXX。

[正文对话...]

晓晓：非常感谢云扬的分享。
云扬：不客气，希望对大家有帮助。
晓晓：下期再见！
```

---

## 🔄 版本历史

- **v1.0** (2026-01-14)
  - ✅ 初始版本
  - ✅ 支持双人对话生成
  - ✅ 支持自定义停顿和语速
  - ✅ 优化段落长度控制

---

## 📧 反馈与建议

如有问题或建议，请联系开发者。

---

**Enjoy! 🎙️**
