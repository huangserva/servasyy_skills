"""
Podcast TTS Generator using shared TTS module
"""
import sys
from pathlib import Path

# 添加共享库路径
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from video.tts import TTSFactory

class PodcastTTSGenerator:
    """播客 TTS 生成器（使用共享模块）"""
    
    def __init__(self, engine='edge-tts', config=None):
        """
        初始化

        Args:
            engine: TTS 引擎 ('edge-tts', 'indextts2', 'minimax')
            config: 引擎配置
        """
        self.engine_name = engine
        self.engine = TTSFactory.create(engine, config)
        self.config = config or {}

        # IndexTTS2 情感映射（与 skill.py 保持一致）
        self.emotion_map = {
            # 英文情感词
            'cheerful': {'vec1': 0.3},
            'angry': {'vec2': 0.3},
            'sad': {'vec3': 1.0},
            'fearful': {'vec4': 1.0},
            'disgruntled': {'vec5': 0.6},
            'serious': {'vec8': 0.7},
            'calm': None,
            'gentle': {'vec8': 0.8, 'vec1': 0.3},
            'chat': None,
            # 中文情感词（兼容旧格式）
            '开心': {'vec1': 1.0},
            '生气': {'vec2': 1.0},
            '悲伤': {'vec3': 1.0},
            '恐惧': {'vec4': 1.0},
            '低落': {'vec6': 1.0},
            '惊喜': {'vec7': 1.0},
            '平静': {'vec8': 1.0},
        }

        # MiniMax 情感映射
        self.minimax_emotion_map = {
            'cheerful': 'happy',
            'chat': 'neutral',
            'calm': 'neutral',
            'serious': 'serious',
            'gentle': 'gentle',
            'fearful': 'fearful',
            'sad': 'sad',
            'angry': 'angry',
            'disgruntled': 'angry'
        }
    
    def generate_dialogues(self, dialogues, output_dir, female_voice='zh-CN-XiaoxiaoNeural',
                          male_voice='zh-CN-YunyangNeural', pause=0.1):
        """
        生成播客对话音频（支持 IndexTTS2 8 维情感向量）

        Args:
            dialogues: 对话列表 [(speaker, text, emotion), ...]
            output_dir: 输出目录
            female_voice: 女声ID
            male_voice: 男声ID
            pause: 对话间停顿（秒）

        Returns:
            (audio_files, temp_files): 音频文件列表
        """
        import os

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"🎤 生成 {len(dialogues)} 个音频片段（{self.engine_name}）...\n")

        audio_files = []
        temp_files = []

        for i, item in enumerate(dialogues, 1):
            # 支持新格式 (speaker, text, emotion) 和旧格式 (speaker, text)
            if len(item) == 3:
                speaker, text, emotion = item
            else:
                speaker, text = item
                emotion = None

            if not text:
                continue

            # 选择声音
            voice = female_voice if speaker == '晓晓' else male_voice

            # 根据引擎选择输出格式
            if self.engine_name == 'indextts2':
                # IndexTTS2 输出 wav 格式
                output_file = output_dir / f'seg_{i:03d}.wav'
            else:
                # Edge TTS 和 MiniMax 输出 mp3 格式
                output_file = output_dir / f'seg_{i:03d}.mp3'

            # 构建显示文本
            display_text = text[:35] + '...' if len(text) > 35 else text
            emo_tag = f"[{list(emotion.keys())[0] if isinstance(emotion, dict) else emotion}]" if emotion else ""
            print(f"   [{i}/{len(dialogues)}] {speaker}{emo_tag}: {display_text}")

            # 构建参数
            kwargs = {}

            # Edge TTS 特定参数（不支持情感）
            if self.engine_name == 'edge-tts':
                # Edge TTS 不支持情感，忽略 emotion
                pass

            # IndexTTS2 特定参数（支持 8 维情感向量）
            elif self.engine_name == 'indextts2':
                if emotion:
                    kwargs['emotion'] = emotion
                # 根据说话人设置参数
                if speaker == '晓晓':
                    kwargs['emo_weight'] = 0.7
                    kwargs['temperature'] = 0.85
                else:
                    kwargs['emo_weight'] = 0.6
                    kwargs['temperature'] = 0.75

            # MiniMax 特定参数（支持简单情感映射）
            elif self.engine_name == 'minimax':
                if emotion:
                    kwargs['emotion'] = self.minimax_emotion_map.get(emotion, 'neutral') if isinstance(emotion, str) else 'neutral'

            # 使用共享 TTS 模块生成
            success = self.engine.generate(
                text=text,
                voice=voice,
                output_path=str(output_file),
                **kwargs
            )

            if success and output_file.exists() and output_file.stat().st_size > 0:
                audio_files.append(str(output_file))
                temp_files.append(str(output_file))
            else:
                print(f"      ⚠️  生成失败，跳过")

        print(f"\n   ✅ 音频生成完成\n")
        return audio_files, temp_files
