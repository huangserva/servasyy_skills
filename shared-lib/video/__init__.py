"""
Video module for shared skills
包含 TTS、动画、视频合成、BGM和模板功能
"""
from .tts import TTSFactory, TTSEngine
from .animation import TextAnimator
from .video_composer import create_video_segment, merge_video_segments
from .subtitle_utils import wrap_text, escape_drawtext
from .dynamic_effects import create_dynamic_video_segment, EFFECTS
from .manim_composer import create_manim_video_segment, MANIM_STYLES, VIDEO_SIZES
from .bgm import add_bgm_to_video, add_bgm_simple, list_available_bgm, BGM_STYLES
from .templates import (
    load_template, list_templates, get_template_style,
    VideoTemplate, SubtitleStyle
)

__all__ = [
    # TTS
    'TTSFactory', 
    'TTSEngine', 
    # Animation
    'TextAnimator',
    # Video Composer
    'create_video_segment',
    'merge_video_segments',
    # Subtitle Utils
    'wrap_text',
    'escape_drawtext',
    # Dynamic Effects
    'create_dynamic_video_segment',
    'EFFECTS',
    # Manim Composer
    'create_manim_video_segment',
    'MANIM_STYLES',
    'VIDEO_SIZES',
    # BGM
    'add_bgm_to_video',
    'add_bgm_simple',
    'list_available_bgm',
    'BGM_STYLES',
    # Templates
    'load_template',
    'list_templates',
    'get_template_style',
    'VideoTemplate',
    'SubtitleStyle',
]
