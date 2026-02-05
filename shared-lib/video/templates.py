"""
视频模板系统
支持加载和应用不同风格的视频模板

模板目录结构：
templates/
├── 9x16/          # 竖屏（抖音）
│   ├── default.yaml
│   ├── elegant.yaml
│   └── minimal.yaml
├── 16x9/          # 横屏（B站）
│   ├── default.yaml
│   └── cinematic.yaml
└── 1x1/           # 方形（小红书）
    └── card.yaml
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass

# 模板目录
TEMPLATES_DIR = Path(__file__).parent / 'templates'


@dataclass
class SubtitleStyle:
    """字幕样式"""
    position: str = 'bottom'        # top / center / bottom
    margin_bottom: float = 0.10     # 距底部比例
    margin_sides: float = 0.075     # 左右边距比例
    max_width: float = 0.85         # 最大宽度比例
    
    font_family: str = 'Heiti SC'
    font_size: int = 80
    font_weight: str = 'ULTRABOLD'
    
    color: str = '#FFFFFF'
    stroke_width: int = 2
    stroke_color: str = '#000000'
    
    animation_style: str = 'write'
    animation_duration_ratio: float = 0.5


@dataclass
class VideoTemplate:
    """视频模板"""
    name: str
    description: str
    aspect_ratio: str
    width: int
    height: int
    subtitle: SubtitleStyle
    background_overlay: Optional[str] = None
    background_blur: int = 0
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'VideoTemplate':
        """从YAML文件加载模板"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 解析字幕配置
        sub_data = data.get('subtitle', {})
        font_data = sub_data.get('font', {})
        stroke_data = sub_data.get('stroke', {})
        anim_data = sub_data.get('animation', {})
        
        subtitle = SubtitleStyle(
            position=sub_data.get('position', 'bottom'),
            margin_bottom=sub_data.get('margin_bottom', 0.10),
            margin_sides=sub_data.get('margin_sides', 0.075),
            max_width=sub_data.get('max_width', 0.85),
            font_family=font_data.get('family', 'Heiti SC'),
            font_size=font_data.get('size', 80),
            font_weight=font_data.get('weight', 'ULTRABOLD'),
            color=sub_data.get('color', '#FFFFFF'),
            stroke_width=stroke_data.get('width', 2),
            stroke_color=stroke_data.get('color', '#000000') or '#000000',
            animation_style=anim_data.get('style', 'write'),
            animation_duration_ratio=anim_data.get('duration_ratio', 0.5),
        )
        
        # 解析分辨率
        res_data = data.get('resolution', {})
        width = res_data.get('width', 1080)
        height = res_data.get('height', 1920)
        
        # 解析背景
        bg_data = data.get('background', {})
        
        return cls(
            name=data.get('name', 'unknown'),
            description=data.get('description', ''),
            aspect_ratio=data.get('aspect_ratio', '9:16'),
            width=width,
            height=height,
            subtitle=subtitle,
            background_overlay=bg_data.get('overlay'),
            background_blur=bg_data.get('blur', 0),
        )


def list_templates(aspect_ratio: Optional[str] = None) -> Dict[str, List[str]]:
    """
    列出可用模板
    
    Args:
        aspect_ratio: 筛选特定比例（'16:9', '9:16', '1:1'）
    
    Returns:
        {比例: [模板名列表]}
    """
    templates = {}
    
    if not TEMPLATES_DIR.exists():
        return templates
    
    ratio_dirs = {
        '16:9': '16x9',
        '9:16': '9x16',
        '1:1': '1x1',
    }
    
    for ratio, dir_name in ratio_dirs.items():
        if aspect_ratio and ratio != aspect_ratio:
            continue
        
        dir_path = TEMPLATES_DIR / dir_name
        if dir_path.exists():
            template_names = [
                f.stem for f in dir_path.glob('*.yaml')
            ]
            if template_names:
                templates[ratio] = template_names
    
    return templates


def load_template(
    name: str = 'default',
    aspect_ratio: str = '9:16'
) -> Optional[VideoTemplate]:
    """
    加载模板
    
    Args:
        name: 模板名称（如 'default', 'elegant', 'cinematic'）
        aspect_ratio: 视频比例
    
    Returns:
        VideoTemplate 对象，失败返回 None
    """
    ratio_dirs = {
        '16:9': '16x9',
        '9:16': '9x16',
        '1:1': '1x1',
    }
    
    dir_name = ratio_dirs.get(aspect_ratio, '9x16')
    template_path = TEMPLATES_DIR / dir_name / f'{name}.yaml'
    
    if not template_path.exists():
        # 尝试 default
        template_path = TEMPLATES_DIR / dir_name / 'default.yaml'
        if not template_path.exists():
            print(f"⚠️ 模板不存在: {name} ({aspect_ratio})")
            return None
    
    try:
        return VideoTemplate.from_yaml(str(template_path))
    except Exception as e:
        print(f"❌ 模板加载失败: {e}")
        return None


def get_default_template(aspect_ratio: str = '9:16') -> VideoTemplate:
    """获取默认模板"""
    template = load_template('default', aspect_ratio)
    if template:
        return template
    
    # 返回硬编码默认值
    return VideoTemplate(
        name='default',
        description='默认模板',
        aspect_ratio=aspect_ratio,
        width=1080 if aspect_ratio != '16:9' else 1920,
        height=1920 if aspect_ratio == '9:16' else (1080 if aspect_ratio in ['16:9', '1:1'] else 1920),
        subtitle=SubtitleStyle(),
    )


# 便捷函数
def get_template_style(
    template_name: str = 'default',
    aspect_ratio: str = '9:16'
) -> Dict[str, Any]:
    """
    获取模板样式配置（简化字典格式）
    
    Returns:
        {
            'width': 1080,
            'height': 1920,
            'font_size': 80,
            'font_weight': 'ULTRABOLD',
            'color': '#FFFFFF',
            'stroke_width': 2,
            'stroke_color': '#000000',
            'animation': 'write',
            'position': 'bottom',
        }
    """
    template = load_template(template_name, aspect_ratio)
    if not template:
        template = get_default_template(aspect_ratio)
    
    return {
        'width': template.width,
        'height': template.height,
        'font_size': template.subtitle.font_size,
        'font_weight': template.subtitle.font_weight,
        'font_family': template.subtitle.font_family,
        'color': template.subtitle.color,
        'stroke_width': template.subtitle.stroke_width,
        'stroke_color': template.subtitle.stroke_color,
        'animation': template.subtitle.animation_style,
        'position': template.subtitle.position,
        'max_width': template.subtitle.max_width,
        'margin_bottom': template.subtitle.margin_bottom,
    }
