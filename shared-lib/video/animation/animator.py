"""
Text Animator using Manim
支持多种文本动画效果和多种视频尺寸
"""
from pathlib import Path
from typing import Literal

# 视频尺寸预设
VIDEO_SIZES = {
    '16:9': (1920, 1080),   # 横屏（B站、YouTube）
    '9:16': (1080, 1920),   # 竖屏（抖音、小红书）
    '1:1': (1080, 1080),    # 方形（小红书、Instagram）
}

class TextAnimator:
    """文本动画生成器"""
    
    def __init__(self, aspect_ratio: Literal['16:9', '9:16', '1:1'] = '16:9'):
        """
        初始化
        
        Args:
            aspect_ratio: 视频比例 ('16:9' 横屏, '9:16' 竖屏, '1:1' 方形)
        """
        self.aspect_ratio = aspect_ratio
        
        # 分辨率配置
        if aspect_ratio in VIDEO_SIZES:
            self.width, self.height = VIDEO_SIZES[aspect_ratio]
        elif aspect_ratio == '16:9':
            self.width = 1920
            self.height = 1080
        else:  # 默认 9:16
            self.width = 1080
            self.height = 1920
    
    def generate_text_animation(
        self,
        text: str,
        duration: float,
        output_path: str,
        style: Literal['fade_in', 'write', 'typewriter', 'slide_in'] = 'fade_in',
        font_size: int = 48,
        color: str = 'WHITE',
        background_color: str = 'BLACK'
    ) -> bool:
        """
        生成文本动画
        
        Args:
            text: 文本内容
            duration: 动画时长（秒）
            output_path: 输出文件路径
            style: 动画风格
                - 'fade_in': 淡入
                - 'write': 手写效果
                - 'typewriter': 打字机效果
                - 'slide_in': 滑入
            font_size: 字体大小
            color: 文字颜色
            background_color: 背景颜色
            
        Returns:
            bool: 是否成功
        """
        try:
            import manim
            from manim import Scene, Text, FadeIn, Write, AddTextLetterByLetter, ImageMobject, VGroup, DOWN, UP, WHITE, BLACK, config
            
            # 创建临时场景类
            class TextScene(Scene):
                def construct(scene_self):
                    # 创建文本对象 - 白色超粗+细黑边框
                    text_obj = Text(
                        text,
                        font_size=80,
                        color='#FFFFFF',
                        font="Heiti SC",
                        weight='ULTRABOLD',
                        stroke_width=2,
                        stroke_color='#000000'
                    )
                    
                    # 自动缩放以适应屏幕宽度（保留15%边距）
                    max_width = config.frame_width * 0.85
                    if text_obj.width > max_width:
                        text_obj.scale_to_fit_width(max_width)
                    
                    # 再往下一点
                    text_obj.shift(DOWN * 8.8)
                    
                    # 应用动画效果
                    if style == 'fade_in':
                        scene_self.play(FadeIn(text_obj), run_time=duration * 0.3)
                        scene_self.wait(duration * 0.7)
                    elif style == 'write':
                        scene_self.play(Write(text_obj), run_time=duration * 0.5)
                        scene_self.wait(duration * 0.5)
                    elif style == 'typewriter':
                        scene_self.play(AddTextLetterByLetter(text_obj), run_time=duration * 0.6)
                        scene_self.wait(duration * 0.4)
                    elif style == 'slide_in':
                        text_obj.shift(DOWN * 3)
                        scene_self.play(text_obj.animate.shift(UP * 3), run_time=duration * 0.4)
                        scene_self.wait(duration * 0.6)
            
            # 配置 Manim
            config.pixel_width = self.width
            config.pixel_height = self.height
            config.frame_rate = 30
            config.background_color = background_color
            config.transparent = True  # 透明背景
            config.format = 'mov'  # 支持alpha通道
            # 输出文件名改为.mov
            output_name = Path(output_path).stem + '.mov'
            config.output_file = output_name
            config.media_dir = str(Path(output_path).parent)
            
            # 渲染场景
            scene = TextScene()
            scene.render()
            
            return True
            
        except ImportError:
            print("❌ Manim 未安装，请运行: pip install manim")
            return False
        except Exception as e:
            print(f"❌ 文本动画生成失败: {e}")
            return False
    
    def generate_subtitle_animation(
        self,
        text: str,
        duration: float,
        output_path: str,
        background_image: str = None
    ) -> bool:
        """
        生成字幕动画（带背景图）
        
        Args:
            text: 字幕文本
            duration: 时长
            output_path: 输出路径
            background_image: 背景图片路径
            
        Returns:
            bool: 是否成功
        """
        try:
            import manim
            from manim import Scene, Text, FadeIn, ImageMobject, VGroup, DOWN, WHITE, BLACK, config
            import numpy as np
            
            class SubtitleScene(Scene):
                def construct(scene_self):
                    # 添加背景图（如果有）
                    if background_image and Path(background_image).exists():
                        bg = ImageMobject(background_image)
                        bg.scale_to_fit_width(config.frame_width)
                        bg.scale_to_fit_height(config.frame_height)
                        scene_self.add(bg)
                    
                    # 创建字幕文本（底部居中）
                    subtitle = Text(
                        text,
                        font_size=56,
                        color=WHITE,
                        font="Heiti SC",
                        stroke_width=4,
                        stroke_color=BLACK
                    ).scale_to_fit_width(config.frame_width * 0.9)
                    
                    # 自动换行
                    if len(text) > 30:
                        lines = []
                        words = text
                        line = ""
                        for char in words:
                            if len(line) < 30:
                                line += char
                            else:
                                lines.append(line)
                                line = char
                        if line:
                            lines.append(line)
                        
                        subtitle = VGroup(*[
                            Text(line, font_size=56, color=WHITE, font="Heiti SC",
                                 stroke_width=4, stroke_color=BLACK)
                            for line in lines
                        ]).arrange(DOWN, buff=0.3)
                    
                    # 位置：底部
                    subtitle.to_edge(DOWN, buff=0.8)
                    
                    # 淡入动画
                    scene_self.play(FadeIn(subtitle), run_time=0.3)
                    scene_self.wait(duration - 0.3)
            
            # 配置
            config.pixel_width = self.width
            config.pixel_height = self.height
            config.frame_rate = 30
            config.background_color = BLACK
            config.output_file = Path(output_path).name
            config.media_dir = str(Path(output_path).parent)
            
            # 渲染
            scene = SubtitleScene()
            scene.render()
            
            return True
            
        except Exception as e:
            print(f"❌ 字幕动画生成失败: {e}")
            return False
