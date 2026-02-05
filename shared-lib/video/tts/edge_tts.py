"""
Edge TTS implementation
"""
import subprocess
import os
from pathlib import Path
from .base import TTSEngine

class EdgeTTSEngine(TTSEngine):
    """Edge TTS 引擎"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.default_voice = self.config.get('default_voice', 'zh-CN-XiaoxiaoNeural')
        self.default_rate = self.config.get('default_rate', '+0%')
    
    def generate(self, text: str, voice: str = None, output_path: str = None, **kwargs) -> bool:
        """使用 Edge TTS 生成音频"""
        if not text:
            return False
        
        voice = voice or self.default_voice
        rate = kwargs.get('rate', self.default_rate)
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 调用 edge-tts
        cmd = [
            'edge-tts',
            '--voice', voice,
            '--rate', rate,
            '--text', text,
            '--write-media', output_path
        ]
        
        # 重试3次
        for attempt in range(3):
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=120, check=True)
                
                # 检查文件是否生成
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return True
                    
            except Exception as e:
                if attempt < 2:
                    import time
                    time.sleep(1)
                    continue
                else:
                    print(f"Edge TTS 生成失败: {e}")
                    return False
        
        return False
