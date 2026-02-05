"""
TTS Engine Factory
"""
from .base import TTSEngine
from .edge_tts import EdgeTTSEngine
from .indextts2 import IndexTTS2Engine
from .minimax import MiniMaxEngine
from .cosyvoice3 import CosyVoice3Engine

class TTSFactory:
    """TTS 引擎工厂"""
    
    _engines = {
        'edge-tts': EdgeTTSEngine,
        'indextts2': IndexTTS2Engine,
        'minimax': MiniMaxEngine,
        'cosyvoice3': CosyVoice3Engine,
    }
    
    @classmethod
    def create(cls, engine_name: str, config: dict = None) -> TTSEngine:
        """
        创建 TTS 引擎实例
        
        Args:
            engine_name: 引擎名称 ('edge-tts', 'indextts2', 'minimax')
            config: 配置字典
            
        Returns:
            TTSEngine: TTS 引擎实例
        """
        engine_class = cls._engines.get(engine_name.lower())
        
        if not engine_class:
            raise ValueError(f"不支持的 TTS 引擎: {engine_name}. 支持: {list(cls._engines.keys())}")
        
        return engine_class(config)
    
    @classmethod
    def list_engines(cls):
        """列出所有支持的引擎"""
        return list(cls._engines.keys())
