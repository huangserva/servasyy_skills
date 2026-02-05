"""
CosyVoice3 TTS Engine
基于阿里通义 Fun-CosyVoice3-0.5B 模型的本地 TTS 引擎
"""
import os
import sys
import tempfile
from pathlib import Path
from .base import TTSEngine


class CosyVoice3Engine(TTSEngine):
    """CosyVoice3 本地 TTS 引擎"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        
        # CosyVoice 安装目录
        self.cosyvoice_dir = self.config.get('cosyvoice_dir', os.path.expanduser('~/CosyVoice'))
        self.model_dir = self.config.get('model_dir', 'pretrained_models/Fun-CosyVoice3-0.5B')
        
        # 参考音频配置
        self.default_prompt_wav = self.config.get('prompt_wav', os.path.join(self.cosyvoice_dir, 'asset/zero_shot_prompt.wav'))
        
        # 英文情感指令映射表（CosyVoice3 对英文指令理解更准确）
        self.emotion_instruction_map = {
            # 修改 angry 为 serious 语气，避免爆音
            'angry': 'Speak in a serious and stern tone.',
            'serious': 'Speak in a serious and stern tone.',
            'sad': 'Speak in a sad and disappointed tone.',
            'calm': 'Speak in a calm and relaxed tone.',
            'gentle': 'Speak in a gentle and warm tone.',
            'chat': 'Speak in a casual and relaxed tone.',
            # excited 也稍微温和一点
            'excited': 'Speak in a happy and energetic tone.',
            'nervous': 'Speak in a nervous and anxious tone.',
            'confused': 'Speak in a confused and puzzled tone.',
            'cheerful': 'Speak in a cheerful and happy tone.',
            'fearful': 'Speak in a fearful and scared tone.',
        }
        
        # 重采样后的参考音频缓存
        self._resampled_cache = {}
        
        # 模型实例（延迟加载）
        self._model = None
        self._loaded = False

    def _ensure_loaded(self):
        """确保模型已加载"""
        if self._loaded:
            return True
            
        try:
            # 添加 CosyVoice 路径
            sys.path.insert(0, self.cosyvoice_dir)
            sys.path.insert(0, os.path.join(self.cosyvoice_dir, 'third_party/Matcha-TTS'))
            
            from cosyvoice.cli.cosyvoice import AutoModel
            
            model_path = os.path.join(self.cosyvoice_dir, self.model_dir)
            if not os.path.exists(model_path):
                print(f"❌ CosyVoice3 模型不存在: {model_path}")
                return False
            
            print("🔄 正在加载 CosyVoice3 模型...")
            self._model = AutoModel(model_dir=model_path)
            self._loaded = True
            print("✅ CosyVoice3 模型加载完成")
            return True
            
        except ImportError as e:
            print(f"❌ CosyVoice3 依赖未安装: {e}")
            print("   请运行: conda activate cosyvoice")
            return False
        except Exception as e:
            print(f"❌ CosyVoice3 加载失败: {e}")
            return False

    def _resample_audio(self, audio_path: str, target_sr: int = 22050) -> str:
        """将参考音频重采样到目标采样率（避免噗呲杂音）"""
        if audio_path in self._resampled_cache:
            return self._resampled_cache[audio_path]
        
        import subprocess
        
        # 创建临时文件
        temp_dir = tempfile.gettempdir()
        filename = os.path.basename(audio_path)
        resampled_path = os.path.join(temp_dir, f"cosyvoice3_{target_sr}_{filename}")
        
        # 如果已经重采样过，直接返回
        if os.path.exists(resampled_path):
            self._resampled_cache[audio_path] = resampled_path
            return resampled_path
        
        # 使用 ffmpeg 重采样
        try:
            subprocess.run([
                'ffmpeg', '-y', '-i', audio_path,
                '-ar', str(target_sr),
                resampled_path
            ], capture_output=True, check=True)
            self._resampled_cache[audio_path] = resampled_path
            return resampled_path
        except Exception:
            # 重采样失败，返回原文件
            return audio_path

    def generate(self, text: str, voice: str = None, output_path: str = None, **kwargs) -> bool:
        """
        使用 CosyVoice3 生成音频
        
        Args:
            text: 要合成的文本
            voice: 参考音频路径（用于零样本克隆）
            output_path: 输出文件路径
            **kwargs:
                emotion: 情感词（如 'angry', 'sad' 等，会自动转换为英文指令）
                instruction: 自定义指令文本（优先级高于 emotion）
                stream: 是否流式生成
        """
        if not text:
            return False
            
        if not self._ensure_loaded():
            return False
        
        try:
            import torchaudio
            
            # 确定参考音频并重采样到 22kHz
            prompt_wav_original = voice if voice and os.path.exists(voice) else self.default_prompt_wav
            prompt_wav = self._resample_audio(prompt_wav_original)
            
            stream = kwargs.get('stream', False)
            
            # 确保输出目录存在
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 确定情感指令（优先使用自定义 instruction，其次用 emotion 映射）
            instruction = kwargs.get('instruction')
            if not instruction:
                emotion = kwargs.get('emotion')
                if emotion:
                    # 如果 emotion 是字典，提取第一个 key
                    if isinstance(emotion, dict):
                        emotion = list(emotion.keys())[0]
                    # 映射到英文指令
                    instruction = self.emotion_instruction_map.get(emotion)
            
            # 始终使用 instruct2 模式（避免 zero_shot 的"故事"问题）
            if instruction:
                instruct_text = f'You are a helpful assistant. {instruction}<|endofprompt|>'
            else:
                instruct_text = 'You are a helpful assistant.<|endofprompt|>'
            
            generator = self._model.inference_instruct2(
                text,
                instruct_text,
                prompt_wav,
                stream=stream
            )
            
            # 生成并保存音频
            for result in generator:
                audio = result['tts_speech']
                
                # 【关键修复】防止爆音/削波
                # 检查最大振幅，如果超过 0.99 则进行归一化处理
                max_val = audio.abs().max()
                if max_val > 0.99:
                    audio = audio / max_val * 0.99
                
                torchaudio.save(output_path, audio, self._model.sample_rate)
                return True
                
            return False
            
        except Exception as e:
            print(f"❌ CosyVoice3 生成失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def generate_async(self, text: str, voice: str = None, output_path: str = None, **kwargs) -> bool:
        """异步生成音频（实际上是同步调用）"""
        return self.generate(text, voice, output_path, **kwargs)
    
    @property
    def sample_rate(self) -> int:
        """返回采样率"""
        if self._model:
            return self._model.sample_rate
        return 22050  # 默认值
