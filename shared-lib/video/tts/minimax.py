"""
MiniMax TTS implementation
"""
import os
import requests
from pathlib import Path
from .base import TTSEngine

class MiniMaxEngine(TTSEngine):
    """MiniMax TTS 引擎"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.api_key = self.config.get('api_key') or os.getenv('MINIMAX_API_KEY')
        self.group_id = self.config.get('group_id') or os.getenv('MINIMAX_GROUP_ID')
        self.api_url = "https://api.minimax.chat/v1/text_to_speech"
        
        # 情感映射
        self.emotion_map = {
            'cheerful': 'happy',
            'chat': 'neutral',
            'calm': 'neutral',
            'serious': 'serious',
            'gentle': 'gentle',
            'fearful': 'fearful',
            'sad': 'sad',
        }
    
    def generate(self, text: str, voice: str = None, output_path: str = None, **kwargs) -> bool:
        """使用 MiniMax TTS 生成音频"""
        if not self.api_key or not self.group_id:
            print("缺少 MiniMax 配置: MINIMAX_API_KEY 和 MINIMAX_GROUP_ID")
            return False

        if not text:
            return False

        # 根据 voice 选择音色
        is_female = 'xiaoxiao' in voice.lower() if voice else True
        voice_id = 'female-tianmei' if is_female else 'male-qn-jingying'

        # 获取情感
        emotion = kwargs.get('emotion', 'neutral')
        emotion_str = self.emotion_map.get(emotion, 'neutral') if emotion else 'neutral'

        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 调用 MiniMax API（与 podcast-generator/skill.py 保持一致）
        url = f"{self.api_url}?GroupId={self.group_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model": "speech-01",
            "voice_id": voice_id,
            "speed": 1.0,
            "vol": 1.0,
            "pitch": 0,
            "emotion": emotion_str,
            "audio_sample_rate": 24000,
            "bitrate": 128000
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)

            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"MiniMax API 错误: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"MiniMax 生成失败: {e}")
            return False
