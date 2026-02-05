# 共享 Video TTS 模块使用说明

## 位置
`~/.claude/skills/shared-lib/video/tts/`

## 支持的引擎

1. **Edge TTS**（默认）
   - 免费，快速
   - 无需配置

2. **IndexTTS2**
   - 声音克隆
   - 需要本地 Gradio 服务
   - 需要参考音频

3. **MiniMax**
   - 商业 API
   - 需要 API Key 和 Group ID

## 使用方式

### Python 代码

```python
from video.tts import TTSFactory

# 创建引擎
engine = TTSFactory.create('edge-tts')

# 生成单个音频
success = engine.generate(
    text="你好，世界",
    voice="zh-CN-XiaoxiaoNeural",
    output_path="output.mp3"
)

# 批量生成
items = [
    {'text': '第一段', 'voice': 'zh-CN-XiaoxiaoNeural', 'output_path': 'audio_001.mp3'},
    {'text': '第二段', 'voice': 'zh-CN-YunyangNeural', 'output_path': 'audio_002.mp3'},
]
audio_files = engine.generate_batch(items)
```

### 命令行

```bash
# image-to-video skill
python ~/.claude/skills/image-to-video/scripts/generate_tts_v2.py \
  --script tts_script.json \
  --output video_output/audio \
  --engine edge-tts

# 使用 IndexTTS2
python generate_tts_v2.py --engine indextts2

# 使用 MiniMax
export MINIMAX_API_KEY="your_key"
export MINIMAX_GROUP_ID="your_group_id"
python generate_tts_v2.py --engine minimax
```

## 配置

### Edge TTS
无需配置，开箱即用。

### IndexTTS2
```python
config = {
    'url': 'http://localhost:7860',
    'female_prompt': '/path/to/female_voice.wav',
    'male_prompt': '/path/to/male_voice.wav'
}
engine = TTSFactory.create('indextts2', config)
```

### MiniMax
```python
config = {
    'api_key': 'your_api_key',
    'group_id': 'your_group_id'
}
engine = TTSFactory.create('minimax', config)
```

或使用环境变量：
```bash
export MINIMAX_API_KEY="your_key"
export MINIMAX_GROUP_ID="your_group_id"
```

## 已集成的 Skills

- ✅ `image-to-video` - 使用 `generate_tts_v2.py`
- ✅ `podcast-generator` - 使用 `tts_generator.py`
- ⏭️ `tts-script-generator` - 不需要（只生成脚本）
