# 视频字幕自动换行 - 永久解决方案

## 问题
之前生成视频时，长字幕不会自动换行，导致显示不全或超出屏幕。

## 解决方案
已在共享库中添加字幕处理工具，**永久解决**字幕换行问题。

## 使用方法

### 方法1：使用封装好的函数（推荐）

```python
import sys
import os
sys.path.append(os.path.expanduser('~/.claude/skills/shared-lib'))

from video.video_composer import create_video_segment, merge_video_segments

# 生成单个视频片段（自动换行）
success = create_video_segment(
    text="这是一段很长的文本，会自动换行显示",
    audio_path="audio.mp3",
    image_path="background.png",
    output_path="segment.mp4",
    width=1080,
    height=1920,  # 9:16竖屏
    font_size=60,
    max_chars_per_line=18  # 每行18个字符
)

# 合并多个片段
segment_files = ["segment_01.mp4", "segment_02.mp4", "segment_03.mp4"]
merge_video_segments(segment_files, "final_video.mp4")
```

### 方法2：单独使用字幕工具

```python
from video.subtitle_utils import wrap_text, escape_drawtext

# 自动换行
text = "这是一段很长的文本需要自动换行显示"
wrapped = wrap_text(text, max_chars_per_line=18)
# 结果: "这是一段很长的文本需要自动\\n换行显示"

# 转义特殊字符（用于ffmpeg drawtext）
escaped = escape_drawtext(wrapped)
```

## 参数说明

### create_video_segment 参数

- `text`: 字幕文本（会自动换行）
- `audio_path`: 音频文件路径
- `image_path`: 背景图片路径
- `output_path`: 输出视频路径
- `width`: 视频宽度（默认1080）
- `height`: 视频高度（默认1920，9:16竖屏）
- `font_size`: 字体大小（默认60）
- `max_chars_per_line`: 每行最大字符数（默认18）
- `font_path`: 字体文件路径（默认PingFang.ttc）

### wrap_text 参数

- `text`: 原始文本
- `max_chars_per_line`: 每行最大字符数（默认18）

## 特性

✅ **自动换行** - 超过指定字符数自动换行  
✅ **居中对齐** - 字幕自动居中显示  
✅ **黑色描边** - 白色字体+黑色描边，任何背景都清晰可见  
✅ **9:16优先** - 默认竖屏，适合抖音/小��书  
✅ **特殊字符转义** - 自动处理冒号、引号等特殊字符  

## 示例：完整视频生成流程

```python
import json
import sys
import os
sys.path.append(os.path.expanduser('~/.claude/skills/shared-lib'))

from video.tts.factory import TTSFactory
from video.video_composer import create_video_segment, merge_video_segments

# 1. 读取脚本
with open('script.json', 'r') as f:
    script = json.load(f)

# 2. 生成TTS音频
tts = TTSFactory.create('edge-tts', {'default_voice': 'zh-CN-YunxiNeural'})
for i, segment in enumerate(script['segments']):
    tts.generate(segment['text'], output_path=f"audio_{i:02d}.mp3")

# 3. 生成视频片段（自动换行字幕）
segment_files = []
for i, segment in enumerate(script['segments']):
    output = f"segment_{i:02d}.mp4"
    success = create_video_segment(
        text=segment['text'],
        audio_path=f"audio_{i:02d}.mp3",
        image_path=f"img_{i:02d}.png",
        output_path=output,
        max_chars_per_line=18  # 自动换行
    )
    if success:
        segment_files.append(output)

# 4. 合并视频
merge_video_segments(segment_files, "final_video.mp4")
```

## 注意事项

1. **字体路径**：macOS默认使用PingFang.ttc，其他系统需要指定正确的中文字体路径
2. **每行字符数**：建议18-20个字符，根据字体大小调整
3. **字幕位置**：默认距离底部300像素，可在video_composer.py中修改

## 更新日志

**2026-01-19**
- ✅ 创建subtitle_utils.py（字幕工具）
- ✅ 创建video_composer.py（视频合成）
- ✅ 更新video模块__init__.py
- ✅ 字幕自动换行功能永久集成到共享库

---

**以后所有视频生成都会自动换行，不需要再手动处理！**
