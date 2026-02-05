#!/usr/bin/env python3
"""
示例：使用共享 video.tts 模块生成播客
"""
import sys
from pathlib import Path

# 添加共享库路径
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from tts_generator import PodcastTTSGenerator

# 示例对话
dialogues = [
    ('晓晓', '欢迎来到《历史不装》，我是晓晓。', 'cheerful'),
    ('云扬', '我是云扬。', 'calm'),
    ('晓晓', '今天咱们聊聊楚汉争霸。', 'chat'),
    ('云扬', '好的，这是一个很有意思的话题。', 'cheerful'),
]

# 使用 Edge TTS（默认）
generator = PodcastTTSGenerator(engine='edge-tts')
audio_files, _ = generator.generate_dialogues(
    dialogues=dialogues,
    output_dir='output/audio',
    female_voice='zh-CN-XiaoxiaoNeural',
    male_voice='zh-CN-YunyangNeural'
)

print(f"\n✅ 生成了 {len(audio_files)} 个音频文件")

# 使用 IndexTTS2（需要本地服务）
# config = {
#     'url': 'http://localhost:7860',
#     'female_prompt': 'female_voice.wav',
#     'male_prompt': 'male_voice.wav'
# }
# generator = PodcastTTSGenerator(engine='indextts2', config=config)

# 使用 MiniMax（需要 API Key）
# import os
# config = {
#     'api_key': os.getenv('MINIMAX_API_KEY'),
#     'group_id': os.getenv('MINIMAX_GROUP_ID')
# }
# generator = PodcastTTSGenerator(engine='minimax', config=config)
