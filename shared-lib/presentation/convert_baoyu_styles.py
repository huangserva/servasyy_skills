#!/usr/bin/env python3
"""
Baoyu 风格转换脚本
将 baoyu-slide-deck 的 .md 风格文件转换为我们的 .yaml 格式
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional


class BaoyuStyleConverter:
    """Baoyu 风格转换器"""
    
    # 风格名称映射（md 文件名 -> 我们的命名规范）
    STYLE_NAME_MAP = {
        'blueprint': 'blueprint',
        'chalkboard': 'chalkboard',
        'notion': 'notion',
        'bold-editorial': 'bold_editorial',
        'corporate': 'corporate',
        'dark-atmospheric': 'dark_atmospheric',
        'editorial-infographic': 'editorial_infographic',
        'fantasy-animation': 'fantasy_animation',
        'intuition-machine': 'intuition_machine',
        'minimal': 'minimal',
        'pixel-art': 'pixel_art',
        'scientific': 'scientific',
        'sketch-notes': 'sketch_notes',
        'vector-illustration': 'vector_illustration',
        'vintage': 'vintage',
        'watercolor': 'watercolor'
    }
    
    # 风格分类
    STYLE_CATEGORIES = {
        'blueprint': 'technical',
        'chalkboard': 'education',
        'notion': 'saas',
        'bold_editorial': 'editorial',
        'corporate': 'business',
        'dark_atmospheric': 'entertainment',
        'editorial_infographic': 'editorial',
        'fantasy_animation': 'creative',
        'intuition_machine': 'technical',
        'minimal': 'minimal',
        'pixel_art': 'gaming',
        'scientific': 'academic',
        'sketch_notes': 'education',
        'vector_illustration': 'creative',
        'vintage': 'historical',
        'watercolor': 'lifestyle'
    }
    
    # 中文显示名
    DISPLAY_NAMES = {
        'blueprint': '技术蓝图',
        'chalkboard': '黑板教学',
        'notion': 'SaaS仪表盘',
        'bold_editorial': '杂志封面',
        'corporate': '企业商务',
        'dark_atmospheric': '暗黑氛围',
        'editorial_infographic': '杂志信息图',
        'fantasy_animation': '奇幻动画',
        'intuition_machine': '技术简报',
        'minimal': '极简主义',
        'pixel_art': '像素艺术',
        'scientific': '科学学术',
        'sketch_notes': '手绘笔记',
        'vector_illustration': '矢量插画',
        'vintage': '复古历史',
        'watercolor': '水彩自然'
    }
    
    def __init__(self, baoyu_styles_dir: Path, output_dir: Path):
        """
        初始化转换器
        
        Args:
            baoyu_styles_dir: baoyu-slide-deck 的 styles 目录
            output_dir: 输出目录（我们的 styles/ 目录）
        """
        self.baoyu_styles_dir = baoyu_styles_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_md_style(self, md_path: Path) -> Dict:
        """
        解析 Markdown 风格文件
        
        Returns:
            {
                'name': str,
                'description': str,
                'design_aesthetic': str,
                'background': str,
                'typography': str,
                'color_palette': str,
                'visual_elements': str,
                'style_rules': str,
                'best_for': str
            }
        """
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = {}
        
        # 提取标题和描述（第一行）
        lines = content.split('\n')
        sections['name'] = lines[0].strip('# ').strip()
        if len(lines) > 2:
            sections['description'] = lines[2].strip()
        
        # 提取各个章节
        section_patterns = {
            'design_aesthetic': r'## Design Aesthetic\s+(.*?)(?=##|\Z)',
            'background': r'## Background\s+(.*?)(?=##|\Z)',
            'typography': r'## Typography\s+(.*?)(?=##|\Z)',
            'color_palette': r'## Color Palette\s+(.*?)(?=##|\Z)',
            'visual_elements': r'## Visual Elements\s+(.*?)(?=##|\Z)',
            'style_rules': r'## Style Rules\s+(.*?)(?=##|\Z)',
            'best_for': r'## Best For\s+(.*?)(?=##|\Z)'
        }
        
        for key, pattern in section_patterns.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                sections[key] = match.group(1).strip()
        
        return sections
    
    def extract_keywords(self, sections: Dict) -> List[str]:
        """从 best_for 提取关键词"""
        best_for = sections.get('best_for', '')
        # 分割逗号分隔的场景
        keywords = [k.strip().lower() for k in best_for.split(',')]
        return [k for k in keywords if k]
    
    def extract_characteristics(self, sections: Dict) -> List[str]:
        """提取特性标签"""
        # 从 design_aesthetic 提取形容词
        aesthetic = sections.get('design_aesthetic', '')
        # 简单提取关键形容词
        chars = []
        if 'clean' in aesthetic.lower():
            chars.append('简洁')
        if 'minimal' in aesthetic.lower():
            chars.append('极简')
        if 'professional' in aesthetic.lower():
            chars.append('专业')
        if 'creative' in aesthetic.lower():
            chars.append('创意')
        if 'technical' in aesthetic.lower():
            chars.append('技术')
        if 'friendly' in aesthetic.lower():
            chars.append('友好')
        if 'elegant' in aesthetic.lower():
            chars.append('优雅')
        
        return chars[:5]  # 最多 5 个
    
    def build_prompt_template(self, sections: Dict, style_name: str) -> str:
        """
        构建提示词模板
        
        将 MD 的各个部分组合成结构化的 prompt
        """
        prompt_parts = [
            f"16:9 landscape aspect ratio, {style_name.upper().replace('_', ' ')} STYLE.",
            ""
        ]
        
        # Design Aesthetic
        if 'design_aesthetic' in sections:
            prompt_parts.append("[DESIGN AESTHETIC]:")
            prompt_parts.append(sections['design_aesthetic'])
            prompt_parts.append("")
        
        # Background
        if 'background' in sections:
            prompt_parts.append("[BACKGROUND]:")
            prompt_parts.append(sections['background'])
            prompt_parts.append("")
        
        # Typography
        if 'typography' in sections:
            prompt_parts.append("[TYPOGRAPHY]:")
            prompt_parts.append(sections['typography'])
            prompt_parts.append("")
        
        # Color Palette
        if 'color_palette' in sections:
            prompt_parts.append("[COLOR PALETTE]:")
            prompt_parts.append(sections['color_palette'])
            prompt_parts.append("")
        
        # Visual Elements
        if 'visual_elements' in sections:
            prompt_parts.append("[VISUAL ELEMENTS]:")
            prompt_parts.append(sections['visual_elements'])
            prompt_parts.append("")
        
        # Style Rules
        if 'style_rules' in sections:
            prompt_parts.append("[STYLE RULES]:")
            prompt_parts.append(sections['style_rules'])
            prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def convert_style(self, md_filename: str) -> Optional[Dict]:
        """
        转换单个风格文件
        
        Args:
            md_filename: MD 文件名（不含路径）
        
        Returns:
            YAML 配置字典
        """
        md_path = self.baoyu_styles_dir / md_filename
        if not md_path.exists():
            print(f"⚠️  文件不存在: {md_path}")
            return None
        
        # 获取风格名称
        base_name = md_path.stem
        style_name = self.STYLE_NAME_MAP.get(base_name, base_name.replace('-', '_'))
        
        print(f"📄 转换: {md_filename} -> {style_name}.yaml")
        
        # 解析 MD
        sections = self.parse_md_style(md_path)
        
        # 构建 YAML 配置
        config = {
            'name': style_name,
            'display_name': self.DISPLAY_NAMES.get(style_name, sections.get('name', style_name)),
            'description': sections.get('description', ''),
            'category': self.STYLE_CATEGORIES.get(style_name, 'general'),
            'prompt_template': self.build_prompt_template(sections, style_name),
            'supports_themes': False,
            'default_theme': None,
            'characteristics': self.extract_characteristics(sections),
            'best_for': self.extract_keywords(sections),
            'keywords': self.extract_keywords(sections),
            'language_notes': {
                'zh': '使用中文字体 PingFang SC',
                'en': 'Use primary font from typography section',
                'ja': '使用 Hiragino Sans'
            },
            'audience_adjustments': {
                'beginners': {
                    'complexity_level': 'low',
                    'explanation_depth': 'high'
                },
                'executives': {
                    'complexity_level': 'medium',
                    'visual_hierarchy': 'strong'
                },
                'experts': {
                    'complexity_level': 'high',
                    'data_density': 'high'
                }
            }
        }
        
        return config
    
    def save_yaml(self, config: Dict, output_filename: str):
        """保存为 YAML 文件"""
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                config,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
                width=100
            )
        
        print(f"   ✅ 保存: {output_path}")
    
    def convert_all(self):
        """批量转换所有风格"""
        print("\n🚀 开始批量转换 Baoyu 风格...\n")
        
        converted_count = 0
        
        for md_name, yaml_name in self.STYLE_NAME_MAP.items():
            md_file = f"{md_name}.md"
            yaml_file = f"{yaml_name}.yaml"
            
            config = self.convert_style(md_file)
            if config:
                self.save_yaml(config, yaml_file)
                converted_count += 1
            
            print()
        
        print(f"\n✅ 转换完成！共转换 {converted_count} 个风格文件")
        print(f"📁 输出目录: {self.output_dir}\n")


def main():
    """主函数"""
    # 路径配置
    baoyu_styles_dir = Path.home() / 'baoyu-skills/skills/baoyu-slide-deck/references/styles'
    output_dir = Path.home() / '.claude/skills/shared-lib/presentation/styles'
    
    print("=" * 60)
    print("Baoyu 风格转换脚本")
    print("=" * 60)
    print(f"\n输入目录: {baoyu_styles_dir}")
    print(f"输出目录: {output_dir}\n")
    
    # 检查输入目录
    if not baoyu_styles_dir.exists():
        print(f"❌ 错误：Baoyu styles 目录不存在: {baoyu_styles_dir}")
        return
    
    # 创建转换器
    converter = BaoyuStyleConverter(baoyu_styles_dir, output_dir)
    
    # 执行转换
    converter.convert_all()
    
    print("=" * 60)
    print("转换完成！现在可以使用新风格了 🎉")
    print("=" * 60)


if __name__ == '__main__':
    main()
