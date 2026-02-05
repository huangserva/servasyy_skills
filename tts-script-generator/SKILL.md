---
name: tts-script-generator
description: Intelligently compress and rewrite documents into TTS-friendly scripts. Uses Claude AI to analyze content, compress to target duration, convert to spoken style with emotional language, and auto-segment. Perfect for video narration.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite
---

# TTS Script Generator

智能压缩和改写文档为适合 TTS 朗读的脚本。

## 核心能力

- 🤖 **AI 智能分析**：Claude 分析文章内容，判断最佳视频时长和配图风格
- ⏱️ **智能时长决策**：根据内容自动决定合适的时长（3-8分钟）
- 🎨 **智能风格决策**：根据主题自动选择配图风格（纽约客/浮世绘/扁平/写实等）
- 📉 **智能压缩**：按最佳时长压缩内容（如 19分钟 → 5分钟）
- 💬 **口语化转换**：书面语 → 自然口语
- 😊 **情感优化**：添加情感词语，让 TTS 更生动
- 🎯 **自动分段**：根据内容自动判断最佳段数（每段 10-20 秒）
- 📊 **时长预估**：精确计算每段朗读时长

## 工作原理

**在 Claude 对话中执行：**
1. Claude 读取原文档
2. Claude 分析内容：
   - 文章主题和结构
   - 核心观点数量
   - 内容密度
   - 判断最佳视频时长（3-8分钟）
   - 判断最适合的配图风格（如：历史类→浮世绘，科技类→扁平，人文类→纽约客）
3. Claude 智能改写：
   - 提取核心观点
   - 按最佳时长压缩
   - 转换为口语化表达
   - 添加情感词语和停顿
4. Claude 自动分段（每段适合配一张图）
5. 根据文章主题判断最适合的配图风格
6. 为每段生成配图描述（使用判断的风格）
7. 输出两个文件：
   - tts_script.json（TTS文本脚本 + 动画标记）
   - visual_config.json（配图描述，供 illustration-generator 使用）

**tts_script.json 格式（新增动画标记）：**
```json
[
  {
    "segment": 1,
    "text": "今天聊聊唐朝真实生活。想穿越？先等等！",
    "duration": 15,
    "animation_style": "fade_in",
    "emphasis": true
  },
  {
    "segment": 2,
    "text": "唐朝可没卫生纸，上厕所用什么？",
    "duration": 12,
    "animation_style": "none",
    "emphasis": false
  }
]
```

**动画标记规则（Claude 智能决策）：**
- `animation_style`: 
  - `"fade_in"` - 标题、开场、重点强调
  - `"write"` - 核心观点、关键结论
  - `"typewriter"` - 数据、事实陈述
  - `"none"` - 普通内容（使用 ASS 字幕）
- `emphasis`: 是否为重点片段（true/false）

**决策原则：**
1. 第1段（开场）→ `fade_in`
2. 核心观���（每个章节的第1段）→ `write`
3. 数据/事实 → `typewriter`
4. 其他内容 → `none`（ASS 字幕）
5. 建议：24段中，3-5段用动画即可

## 执行脚本

### generate.py - 生成 TTS 脚本
```bash
python ~/.claude/skills/tts-script-generator/scripts/generate.py <markdown文件>
```
- 读取 Markdown 文件
- 提取 H2 章节
- 转换为口语化
- 按时长分割
- 输出 `tts_script.json`

## 使用场景

1. **视频配音**：配合 image-to-video（主要用途）
2. **播客生成**：配合 podcast-generator

## 输出说明

**本 skill 输出：**
- ✅ `tts_script.json` - TTS 文本脚本
- ✅ `visual_config.json` - 配图描述

**不包含：**
- ❌ TTS 音频生成（由 image-to-video skill 负责）
- ❌ 配图生成（需调用 illustration-generator skill）
- ❌ 视频合成（需调用 image-to-video skill）

## 调用方式

**由 image-to-video skill 自动调用：**
```
image-to-video 检测到长文档 
  → 调用 tts-script-generator
  → Claude 在对话中改写
  → 输出压缩后的 TTS 脚本
  → image-to-video 继续处理
```

**手动调用（在 Claude 对话中）：**
```
用户: "请用 tts-script-generator 改写这篇文章"

Claude: 
1. 读取文档（5947 字，19 分钟）
2. 分析内容：
   - 主题：唐朝生活科普（历史人文类）
   - 核心观点：4个（卫生、饮食、管制、阶级）
   - 判断最佳时长：5 分钟（内容密度适中）
   - 判断配图风格：浮世绘风格（历史题材，东方古典美学）
3. 改写为 1350 字
4. 分成 20 段（每段 15 秒）
5. 为每段生成浮世绘风格配图描述
6. 保存 tts_script.json + visual_config.json
```

## 输出格式

### tts_script.json
```json
[
  {
    "segment": 1,
    "text": "今天聊聊唐朝真实生活。想穿越？先等等！唐朝可没卫生纸...",
    "duration": 15
  }
]
```

### visual_config.json
```json
{
  "article_title": "穿越唐朝的真相",
  "style": "ukiyo-e",
  "sections": [
    {
      "section": 1,
      "visual_description": "A person standing at a crossroads between modern city and ancient Tang Dynasty palace, looking confused, ukiyo-e style with traditional Japanese woodblock print aesthetics"
    }
  ]
}
```

## 配图风格决策规则

Claude 会根据文章主题自动选择最适合的风格：

- **历史/古典类** → `ukiyo-e`（浮世绘）：唐朝、宋朝、日本历史等
- **人文/社会类** → `new-yorker`（纽约客）：社会观察、人物故事等
- **科技/商业类** → `flat`（扁平风格）：科技产品、商业分析等
- **自然/旅行类** → `realistic`（写实风格）：风景、动物、旅行等
- **艺术/创意类** → `abstract`（抽象风格）：艺术评论、创意思考等

## 改写原则

1. **保留核心**：保留最重要的观点和故事
2. **口语化**：
   - "但是" → "但是呢"
   - "因为...所以..." → "为什么呢？因为..."
   - 添加语气词："啊"、"呢"、"吧"
3. **情感词语**：
   - 强调："真的"、"非常"、"特别"
   - 惊叹："哇"、"天哪"、"想象一下"
4. **节奏控制**：
   - 短句为主
   - 适当停顿
   - 每段一个核心点

## 可被调用

- image-to-video skill（主要）
- podcast-generator skill
- 其他需要 TTS 的 skills
