"""
Base TTS Engine interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class TTSEngine(ABC):
    """TTS 引擎基类"""
    
    @abstractmethod
    def generate(self, text: str, voice: str, output_path: str, **kwargs) -> bool:
        """
        生成单个音频
        
        Args:
            text: 文本内容
            voice: 语音ID
            output_path: 输出文件路径
            **kwargs: 其他参数（如情感、语速等）
            
        Returns:
            bool: 是否成功
        """
        pass
    
    def generate_batch(self, items: List[Dict]) -> List[str]:
        """
        批量生成音频
        
        Args:
            items: 列表，每项包含 {text, voice, output_path, ...}
            
        Returns:
            List[str]: 成功生成的音频文件路径列表
        """
        audio_files = []
        for item in items:
            text = item.get('text', '')
            voice = item.get('voice', '')
            output_path = item.get('output_path', '')
            
            if self.generate(text, voice, output_path, **item):
                audio_files.append(output_path)
        
        return audio_files
