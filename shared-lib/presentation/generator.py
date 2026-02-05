"""
PPT生成器
支持 Style × Theme × Layout 三维组合系统
"""
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple


# 模块目录
MODULE_DIR = Path(__file__).parent
STYLES_DIR = MODULE_DIR / 'styles'
LAYOUTS_DIR = MODULE_DIR / 'layouts'
THEMES_DIR = MODULE_DIR / 'themes'


class PresentationGenerator:
    """PPT生成器，支持风格、主题和布局组合（增强版）"""
    
    def __init__(
        self,
        style: str = 'apple',
        theme: Optional[str] = 'soft_blue',
        session_id: Optional[str] = None,
        language: str = 'zh',
        audience: str = 'general',
        provider: str = 'auto',
        render_mode: str = 'full_image'  # 新增：'full_image' 或 'background'
    ):
        """
        初始化生成器
        
        Args:
            style: 视觉风格（22 种可选，如 apple/blueprint/notion/chalkboard 等）
            theme: 颜色主题（仅 apple 风格支持，如 soft_blue/elegant_purple 等）
            session_id: 会话ID，保持多页风格一致（可选）
            language: 语言代码（zh/en/ja/...）
            audience: 目标受众（beginners/intermediate/experts/executives/general）
            provider: 图像API provider
            render_mode: 渲染模式
                - 'full_image': AI直接生成带文字的完整图片（效果更好）
                - 'background': 只生成纯背景，后期叠加文字（可编辑）
        """
        self.style = style
        self.theme = theme if style == 'apple' else None
        self.session_id = session_id
        self.language = language
        self.audience = audience
        self.provider = provider
        self.render_mode = render_mode
        
        self._styles_cache: Dict[str, Dict] = {}
        self._layouts_cache: Dict[str, Dict] = {}
        self._themes_cache: Dict[str, Dict] = {}
        
        # 如果提供了 session_id，尝试加载会话
        self._session_manager = None
        if session_id:
            try:
                from .session_manager import SessionManager
                self._session_manager = SessionManager.load_session(session_id)
                if self._session_manager:
                    # 从会话加载配置
                    meta = self._session_manager.get_metadata()
                    self.style = meta.get('style', style)
                    self.theme = meta.get('theme', theme)
                    self.language = meta.get('language', language)
                    self.audience = meta.get('audience', audience)
            except ImportError:
                pass
    
    def list_styles(self) -> List[str]:
        """列出所有可用风格"""
        return [f.stem for f in STYLES_DIR.glob('*.yaml')]
    
    def list_layouts(self) -> List[str]:
        """列出所有可用布局"""
        return [f.stem for f in LAYOUTS_DIR.glob('*.yaml')]
    
    def list_themes(self) -> List[str]:
        """列出所有可用主题"""
        return [f.stem for f in THEMES_DIR.glob('*.yaml')]
    
    def get_style_info(self, style: str) -> Optional[Dict[str, Any]]:
        """获取风格详情"""
        return self._load_style(style)
    
    def get_layout_info(self, layout: str) -> Optional[Dict[str, Any]]:
        """获取布局详情"""
        return self._load_layout(layout)
    
    def get_theme_info(self, theme: str) -> Optional[Dict[str, Any]]:
        """获取主题详情"""
        return self._load_theme(theme)
    
    def _load_style(self, style: str) -> Optional[Dict[str, Any]]:
        """加载风格配置"""
        if style in self._styles_cache:
            return self._styles_cache[style]
        
        style_path = STYLES_DIR / f'{style}.yaml'
        if not style_path.exists():
            print(f"⚠️ 风格不存在: {style}")
            return None
        
        try:
            with open(style_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self._styles_cache[style] = config
            return config
        except Exception as e:
            print(f"❌ 加载风格失败: {e}")
            return None
    
    def _load_layout(self, layout: str) -> Optional[Dict[str, Any]]:
        """加载布局配置"""
        if layout in self._layouts_cache:
            return self._layouts_cache[layout]
        
        layout_path = LAYOUTS_DIR / f'{layout}.yaml'
        if not layout_path.exists():
            print(f"⚠️ 布局不存在: {layout}")
            return None
        
        try:
            with open(layout_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self._layouts_cache[layout] = config
            return config
        except Exception as e:
            print(f"❌ 加载布局失败: {e}")
            return None
    
    def _load_theme(self, theme: str) -> Optional[Dict[str, Any]]:
        """加载主题配置"""
        if theme in self._themes_cache:
            return self._themes_cache[theme]
        
        theme_path = THEMES_DIR / f'{theme}.yaml'
        if not theme_path.exists():
            print(f"⚠️ 主题不存在: {theme}")
            return None
        
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self._themes_cache[theme] = config
            return config
        except Exception as e:
            print(f"❌ 加载主题失败: {e}")
            return None
    
    def build_slide_prompt(
        self,
        layout: str = 'cover',
        content: str = '',
        title: str = '',
        subtitle: str = '',
        left_content: str = '',
        right_content: str = '',
        extra_instructions: str = ''
    ) -> str:
        """
        构建幻灯片生成提示词
        
        Args:
            layout: 布局类型（cover/section_divider/content_left/content_center/content_two_column）
            content: 内容描述（用于要点列表等）
            title: 标题文字（用于 full_image 模式）
            subtitle: 副标题文字（用于 cover 布局）
            left_content: 左栏内容（用于 two_column 布局）
            right_content: 右栏内容（用于 two_column 布局）
            extra_instructions: 额外指令
        
        Returns:
            组合后的完整prompt
        """
        style_config = self._load_style(self.style)
        layout_config = self._load_layout(layout)
        theme_config = self._load_theme(self.theme) if self.theme else None
        
        if not style_config:
            style_config = self._load_style('apple')
        if not layout_config:
            layout_config = self._load_layout('cover')
        
        # 获取风格描述
        style_description = ""
        if style_config and 'prompt_template' in style_config:
            style_description = style_config['prompt_template'].strip()
        
        # 获取主题描述
        theme_description = ""
        if theme_config and 'description_template' in theme_config:
            theme_description = theme_config['description_template'].strip()
        
        # 根据 render_mode 选择模板
        if self.render_mode == 'full_image' and 'prompt_template_full' in layout_config:
            template_key = 'prompt_template_full'
        else:
            template_key = 'prompt_template'
        
        # 获取布局prompt模板
        layout_prompt = ""
        if layout_config and template_key in layout_config:
            layout_prompt = layout_config[template_key].strip()
            
            # 替换风格和主题占位符
            layout_prompt = layout_prompt.replace('{style_description}', style_description)
            layout_prompt = layout_prompt.replace('{theme_description}', theme_description)
            
            # 替换文字占位符（full_image 模式）
            if self.render_mode == 'full_image':
                # 智能解析 title：如果没有提供，从 content 第一行提取
                actual_title = title
                actual_subtitle = subtitle
                actual_content = content
                
                if not actual_title and content:
                    lines = content.strip().split('\n')
                    actual_title = lines[0].strip()
                    if len(lines) > 1:
                        # 剩余内容作为 content 或 subtitle
                        remaining = '\n'.join(lines[1:]).strip()
                        if layout == 'cover' and not actual_subtitle:
                            actual_subtitle = remaining
                        elif not actual_content or actual_content == content:
                            actual_content = remaining
                
                # 替换占位符
                layout_prompt = layout_prompt.replace('{title}', actual_title or '')
                layout_prompt = layout_prompt.replace('{subtitle}', actual_subtitle or '')
                layout_prompt = layout_prompt.replace('{content}', actual_content or '')
                layout_prompt = layout_prompt.replace('{left_content}', left_content or '')
                layout_prompt = layout_prompt.replace('{right_content}', right_content or '')
        
        # 组合最终prompt
        parts = [layout_prompt]
        
        # background 模式下，添加 content context
        if self.render_mode == 'background' and content:
            parts.append(f"Content context: {content}")
        
        # 添加受众适配指令
        audience_instructions = self._get_audience_instructions()
        if audience_instructions:
            parts.append(audience_instructions)
        
        if extra_instructions:
            parts.append(f"Extra requirements: {extra_instructions}")
        
        return '\n\n'.join(parts)
    
    def _get_audience_instructions(self) -> str:
        """根据受众类型返回适配指令"""
        audience_map = {
            'beginners': """## Audience Adaptation: Beginners
- One concept per slide
- Visual metaphors over abstract diagrams
- Simple language, no jargon
- Generous whitespace, low density""",
            'intermediate': """## Audience Adaptation: Intermediate
- Balanced information density
- Some technical terms acceptable
- Structured, clear progression""",
            'experts': """## Audience Adaptation: Experts
- High information density acceptable
- Technical diagrams with precise labels
- Assume domain knowledge
- Data-rich, precise content""",
            'executives': """## Audience Adaptation: Executives
- Lead with insights, not data
- "So what?" on every slide
- Decision-enabling content
- Bottom-line upfront (BLUF)
- Clean, impactful visuals""",
            'general': ""  # 通用受众不添加额外指令
        }
        return audience_map.get(self.audience, "")
    
    def generate_slide(
        self,
        layout: str = 'cover',
        content: str = '',
        output_path: Optional[str] = None,
        extra_instructions: str = '',
        max_retries: int = 2
    ) -> Tuple[str, str]:
        """
        生成单个幻灯片背景
        
        Args:
            layout: 布局类型
            content: 内容描述
            output_path: 输出路径（可选）
            extra_instructions: 额外指令
            max_retries: 最大重试次数
        
        Returns:
            (image_url, provider)
        """
        # 构建prompt
        full_prompt = self.build_slide_prompt(layout, content, extra_instructions)
        
        print(f"🎨 生成幻灯片: style={self.style}, theme={self.theme}, layout={layout}")
        
        # 调用底层API
        import sys
        sys.path.insert(0, str(MODULE_DIR.parent))
        from image_api import ImageGenerator
        
        generator = ImageGenerator(provider=self.provider)
        
        try:
            image_url, used_provider = generator.generate_raw_style(
                prompt=full_prompt,
                aspect_ratio='16:9',
                max_retries=max_retries
            )
            
            if output_path:
                generator.save_image(image_url, output_path)
                print(f"✅ 幻灯片已保存: {output_path}")
            
            return (image_url, used_provider)
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            raise
    
    def get_layout_text_zones(self, layout: str) -> List[Dict]:
        """
        获取布局的文字区域定义
        
        Args:
            layout: 布局类型
        
        Returns:
            文字区域列表
        """
        layout_config = self._load_layout(layout)
        if layout_config and 'text_zones' in layout_config:
            return layout_config['text_zones']
        return []
    
    def regenerate_slide(
        self,
        ppt_dir: str,
        slide_number: int,
        new_content: Optional[str] = None,
        new_layout: Optional[str] = None,
        extra_instructions: str = ''
    ) -> Tuple[str, str]:
        """
        单页修改：重新生成指定幻灯片
        
        Args:
            ppt_dir: PPT工作目录（包含 slide_XX.png 和 ppt_content.yaml）
            slide_number: 要重新生成的页码（从1开始）
            new_content: 新的内容描述（可选，不提供则用原内容）
            new_layout: 新的布局（可选，不提供则用原布局）
            extra_instructions: 额外指令
        
        Returns:
            (image_url, provider)
        """
        import os
        
        ppt_path = Path(ppt_dir)
        
        # 读取原始配置（如果存在）
        config_file = ppt_path / 'ppt_content.yaml'
        original_config = None
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    original_config = yaml.safe_load(f)
            except Exception:
                pass
        
        # 确定布局和内容
        layout = new_layout
        content = new_content or ''
        
        if original_config and 'slides' in original_config:
            slides = original_config['slides']
            if 0 < slide_number <= len(slides):
                slide_info = slides[slide_number - 1]
                if not layout:
                    layout = slide_info.get('layout', 'content_left')
                if not new_content:
                    content = slide_info.get('content', '')
        
        # 默认布局
        if not layout:
            if slide_number == 1:
                layout = 'cover'
            else:
                layout = 'content_left'
        
        print(f"🔄 重新生成幻灯片 #{slide_number}: layout={layout}")
        
        # 生成新图片
        output_path = ppt_path / f'slide_{slide_number:02d}.png'
        
        image_url, provider = self.generate_slide(
            layout=layout,
            content=content,
            output_path=str(output_path),
            extra_instructions=extra_instructions
        )
        
        print(f"✅ 幻灯片 #{slide_number} 已重新生成")
        
        return (image_url, provider)
    
    def batch_generate_slides(
        self,
        slides_config: List[Dict],
        output_dir: str,
        parallel: bool = True,
        max_workers: int = 3
    ) -> List[Tuple[int, str, str]]:
        """
        批量生成幻灯片
        
        Args:
            slides_config: 幻灯片配置列表
                [{'layout': 'cover', 'content': '标题'}, {'layout': 'content_left', 'content': '内容'}, ...]
            output_dir: 输出目录
            parallel: 是否并行生成
            max_workers: 最大并行数
        
        Returns:
            [(slide_number, image_url, provider), ...]
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import os
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        def generate_one(idx: int, config: Dict) -> Tuple[int, str, str]:
            layout = config.get('layout', 'content_left')
            content = config.get('content', '')
            extra = config.get('extra_instructions', '')
            
            slide_path = output_path / f'slide_{idx:02d}.png'
            
            image_url, provider = self.generate_slide(
                layout=layout,
                content=content,
                output_path=str(slide_path),
                extra_instructions=extra
            )
            
            return (idx, image_url, provider)
        
        if parallel and len(slides_config) > 1:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(generate_one, idx + 1, config): idx + 1
                    for idx, config in enumerate(slides_config)
                }
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                        print(f"   完成幻灯片 #{result[0]}")
                    except Exception as e:
                        slide_num = futures[future]
                        print(f"   ❌ 幻灯片 #{slide_num} 失败: {e}")
        else:
            for idx, config in enumerate(slides_config, 1):
                try:
                    result = generate_one(idx, config)
                    results.append(result)
                except Exception as e:
                    print(f"   ❌ 幻灯片 #{idx} 失败: {e}")
        
        # 按页码排序
        results.sort(key=lambda x: x[0])
        
        # 保存配置
        config_file = output_path / 'ppt_content.yaml'
        save_config = {
            'style': self.style,
            'theme': self.theme,
            'slides': [
                {'slide_number': idx + 1, **config}
                for idx, config in enumerate(slides_config)
            ]
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(save_config, f, allow_unicode=True)
        
        print(f"✅ 批量生成完成: {len(results)}/{len(slides_config)} 张幻灯片")
        
        return results


def list_styles() -> List[str]:
    """列出所有可用风格"""
    return PresentationGenerator().list_styles()


def list_layouts() -> List[str]:
    """列出所有可用布局"""
    return PresentationGenerator().list_layouts()


def list_themes() -> List[str]:
    """列出所有可用主题"""
    return PresentationGenerator().list_themes()


if __name__ == '__main__':
    # 测试
    gen = PresentationGenerator(style='apple', theme='soft_blue')
    
    print("可用风格:", gen.list_styles())
    print("可用布局:", gen.list_layouts())
    print("可用主题:", gen.list_themes())
    
    # 测试prompt构建
    prompt = gen.build_slide_prompt(
        layout='cover',
        content='AI技术趋势报告'
    )
    print("\n生成的Prompt:")
    print(f"长度: {len(prompt)} 字符")
    print(f"前500字符:\n{prompt[:500]}...")
    
    # 测试获取文字区域
    zones = gen.get_layout_text_zones('cover')
    print(f"\n封面布局文字区域: {len(zones)} 个")
    for zone in zones:
        print(f"  - {zone['name']}: {zone['position']}")
