"""
IndexTTS2 implementation
支持 IndexTTS2 Gradio Web UI 模式（8维情感向量控制）
"""
import os
import shutil
from pathlib import Path
from .base import TTSEngine


class IndexTTS2Engine(TTSEngine):
    """IndexTTS2 引擎（通过 Gradio Web UI，支持情感向量）"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        import os
        self.url = self.config.get('url', os.environ.get('INDEXTTS2_URL', 'http://219.147.109.250:7860')).rstrip('/')

        # 默认使用 shared-lib/voices 目录下的参考音频
        voices_dir = Path(__file__).parent.parent.parent / 'voices'
        self.female_prompt = self.config.get('female_prompt', os.environ.get('INDEXTTS2_FEMALE_PROMPT', str(voices_dir / 'female.wav')))
        self.male_prompt = self.config.get('male_prompt', os.environ.get('INDEXTTS2_MALE_PROMPT', str(voices_dir / 'male.wav')))

        # 情感映射（与 podcast-generator/skill.py 保持一致）
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

    def generate(self, text: str, voice: str = None, output_path: str = None, **kwargs) -> bool:
        """使用 IndexTTS2 Gradio Web UI 生成音频（支持情感向量）"""
        if not text:
            return False

        try:
            from gradio_client import Client, handle_file
        except ImportError:
            print("❌ 需要安装 gradio_client: pip install gradio_client")
            return False

        # 根据 voice 选择参考音频
        # 如果 voice 是文件路径且存在，直接使用；否则按 female/male 判断
        is_female = True  # 默认值
        if voice and os.path.exists(voice):
            prompt_audio = voice
            # 根据路径判断是否女声
            is_female = 'female' in voice.lower()
        elif voice:
            voice_lower = voice.lower()
            is_female = ('female' in voice_lower or 
                         'xiaoyi' in voice_lower or  # 修复：xiaoyi 不是 xiaoxiao
                         'xiaoxiao' in voice_lower)
            prompt_audio = self.female_prompt if is_female else self.male_prompt
        else:
            prompt_audio = self.female_prompt

        if not prompt_audio or not os.path.exists(prompt_audio):
            print(f"IndexTTS2 参考音频不存在: {prompt_audio}")
            return False

        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            # 连接到 Gradio 服务
            client = Client(self.url, httpx_kwargs={"timeout": 300.0})
        except Exception as e:
            print(f"   ❌ 无法连接到 IndexTTS2 服务: {e}\n")
            return False

        # 解析情感参数
        emotion = kwargs.get('emotion')
        vec = {'vec1': 0, 'vec2': 0, 'vec3': 0, 'vec4': 0,
               'vec5': 0, 'vec6': 0, 'vec7': 0, 'vec8': 0}
        emo_method = "与音色参考音频相同"

        if emotion:
            if isinstance(emotion, dict):
                # 直接传入向量字典
                vec.update(emotion)
                emo_method = "使用情感向量控制"
            else:
                # 使用预定义情感
                mapped = self.emotion_map.get(emotion)
                if mapped:
                    vec.update(mapped)
                    emo_method = "使用情感向量控制"

        # 根据说话人选择参数
        if is_female:
            emo_weight = kwargs.get('emo_weight', 0.7)
            temperature = kwargs.get('temperature', 0.85)
        else:
            emo_weight = kwargs.get('emo_weight', 0.6)
            temperature = kwargs.get('temperature', 0.75)

        # 如果有参考音频，使用 handle_file
        prompt = handle_file(prompt_audio) if prompt_audio and os.path.exists(prompt_audio) else None

        try:
            # 调用 Gradio predict API（与 podcast-generator/skill.py 保持一致）
            result = client.predict(
                emo_control_method=emo_method,
                prompt=prompt,
                text=text,
                emo_ref_path=None,
                emo_weight=emo_weight,
                vec1=vec['vec1'], vec2=vec['vec2'], vec3=vec['vec3'], vec4=vec['vec4'],
                vec5=vec['vec5'], vec6=vec['vec6'], vec7=vec['vec7'], vec8=vec['vec8'],
                emo_text="",
                emo_random=False,
                max_text_tokens_per_segment=120,
                param_16=True,
                param_17=0.8,
                param_18=30,
                param_19=temperature,
                param_20=0.0,
                param_21=3,
                param_22=10.0,
                param_23=1500,
                api_name="/generate"
            )

            # 复制生成的音频文件
            audio_path = result.get('value') if isinstance(result, dict) else result
            if audio_path and os.path.exists(audio_path):
                shutil.copy(audio_path, output_path)
                return True
            else:
                print(f"IndexTTS2 未返回有效的音频文件")
                return False

        except Exception as e:
            print(f"IndexTTS2 生成失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def generate_async(self, text: str, voice: str = None, output_path: str = None, **kwargs) -> bool:
        """异步生成音频"""
        return self.generate(text, voice, output_path, **kwargs)
