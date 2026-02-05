"""
PPT 风格工具函数

只提供风格列表、信息查询等工具函数。
风格选择逻辑由 AI 根据 ppt-generator/SKILL.md 完成。
"""
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any


# 模块目录
MODULE_DIR = Path(__file__).parent
STYLES_DIR = MODULE_DIR / 'styles'
THEMES_DIR = MODULE_DIR / 'themes'


class StyleSelector:
    """PPT 风格工具类（仅提供查询功能）"""

    def __init__(self):
        """初始化"""
        self._styles_cache: Dict[str, Dict] = {}
        self._themes_cache: Dict[str, Dict] = {}

    def list_styles(self) -> List[str]:
        """列出所有可用风格"""
        return sorted([f.stem for f in STYLES_DIR.glob('*.yaml')])

    def list_themes(self) -> List[str]:
        """列出所有可用主题（仅 apple 风格使用）"""
        return sorted([f.stem for f in THEMES_DIR.glob('*.yaml')])

    def get_style_info(self, style: str) -> Optional[Dict[str, Any]]:
        """
        获取风格详情
        
        Args:
            style: 风格名称
            
        Returns:
            风格配置字典，包含 name, description, prompt_template 等
        """
        if style in self._styles_cache:
            return self._styles_cache[style]
        
        style_path = STYLES_DIR / f'{style}.yaml'
        if not style_path.exists():
            return None
        
        try:
            with open(style_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self._styles_cache[style] = config
            return config
        except Exception:
            return None

    def get_theme_info(self, theme: str) -> Optional[Dict[str, Any]]:
        """
        获取主题详情
        
        Args:
            theme: 主题名称
            
        Returns:
            主题配置字典
        """
        if theme in self._themes_cache:
            return self._themes_cache[theme]
        
        theme_path = THEMES_DIR / f'{theme}.yaml'
        if not theme_path.exists():
            return None
        
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self._themes_cache[theme] = config
            return config
        except Exception:
            return None

    def style_exists(self, style: str) -> bool:
        """检查风格是否存在"""
        return (STYLES_DIR / f'{style}.yaml').exists()

    def theme_exists(self, theme: str) -> bool:
        """检查主题是否存在"""
        return (THEMES_DIR / f'{theme}.yaml').exists()


# 便捷函数
def list_styles() -> List[str]:
    """列出所有可用风格"""
    return StyleSelector().list_styles()


def list_themes() -> List[str]:
    """列出所有可用主题"""
    return StyleSelector().list_themes()


def list_layouts() -> List[str]:
    """列出所有可用布局"""
    layouts_dir = MODULE_DIR / 'layouts'
    if layouts_dir.exists():
        return sorted([f.stem for f in layouts_dir.glob('*.yaml')])
    return []


def get_style_info(style: str) -> Optional[Dict[str, Any]]:
    """获取风格详情"""
    return StyleSelector().get_style_info(style)


def get_theme_info(theme: str) -> Optional[Dict[str, Any]]:
    """获取主题详情"""
    return StyleSelector().get_theme_info(theme)
