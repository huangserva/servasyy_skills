#!/usr/bin/env python3
"""
Markdown Illustrator - 为Markdown文档自动配图

使用方式:
    python3 illustrate.py <markdown_file> [options]

示例:
    # 使用默认设置（5张纽约客风格配图）
    python3 illustrate.py article.md
    
    # 指定风格和数量
    python3 illustrate.py article.md --style ukiyoe --num 3
    
    # 自定义provider优先级
    python3 illustrate.py article.md --priority modelscope,google-local,zimage
"""

import sys
import os
import re
import argparse
from pathlib import Path

# 添加shared-lib到路径
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from image_api import ImageGenerator


class MarkdownIllustrator:
    """Markdown文档配图工具"""
    
    def __init__(self, style='newyorker', provider='auto', custom_priority=None):
        """
        初始化配图工具
        
        Args:
            style: 图片风格 ('newyorker', 'ukiyoe')
            provider: 图片生成provider
            custom_priority: 自定义优先级列表
        """
        self.style = style
        self.generator = ImageGenerator(provider=provider, custom_priority=custom_priority)
    
    def analyze_markdown(self, markdown_path):
        """
        分析Markdown文档结构
        
        Returns:
            dict: {
                'title': 文章标题,
                'sections': [章节列表],
                'content': 完整内容
            }
        """
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # 提取标题和章节
        title = None
        sections = []
        
        for line in lines:
            # H1标题
            if line.startswith('# ') and not title:
                title = re.sub(r'^#\s*', '', line).strip()
            
            # H2章节
            elif line.startswith('## '):
                section_title = re.sub(r'^##\s*', '', line).strip()
                # 移除emoji
                section_title = re.sub(r'[📍🌙⚔️💡🎯✨🎬🔥⚡️🌟💎🎨🎭🎪]', '', section_title).strip()
                if section_title:
                    sections.append(section_title)
        
        return {
            'title': title or 'Untitled',
            'sections': sections,
            'content': content
        }
    
    def generate_visual_strategies(self, sections, num_images=None):
        """
        为章节生成视觉描述策略
        
        Args:
            sections: 章节列表
            num_images: 生成图片数量（None=自动）
        
        Returns:
            list: [(section_title, visual_strategy, caption), ...]
        """
        if num_images is None:
            num_images = min(len(sections), 5)  # 默认最多5张
        
        # 简单策略：为前N个章节配图
        strategies = []
        
        for i, section in enumerate(sections[:num_images]):
            # 这里可以接入LLM生成更智能的视觉描述
            # 目前使用简单的模板
            visual_strategy = f"An illustration representing: {section}"
            caption = section
            
            strategies.append((section, visual_strategy, caption))
        
        return strategies
    
    def generate_images(self, strategies, output_dir):
        """
        生成图片
        
        Args:
            strategies: 视觉策略列表
            output_dir: 输出目录
        
        Returns:
            list: [(section_title, image_path, provider), ...]
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        print(f"\n{'='*60}")
        print(f"🎨 开始生成 {len(strategies)} 张配图")
        print(f"   风格: {self.style}")
        print(f"   输出目录: {output_dir}")
        print(f"{'='*60}\n")
        
        for i, (section, visual_strategy, caption) in enumerate(strategies, 1):
            print(f"\n[{i}/{len(strategies)}] {section}")
            print(f"{'─'*60}")
            
            try:
                # 根据风格调用不同的生成方法
                if self.style == 'newyorker':
                    image_url, provider = self.generator.generate_newyorker_style(
                        visual_strategy=visual_strategy,
                        caption=caption,
                        max_retries=1
                    )
                elif self.style == 'ukiyoe':
                    image_url, provider = self.generator.generate_ukiyoe_style(
                        visual_strategy=visual_strategy,
                        caption=caption,
                        max_retries=1
                    )
                else:
                    raise ValueError(f"不支持的风格: {self.style}")
                
                # 保存图片
                output_path = output_dir / f"img_{i:03d}.jpg"
                self.generator.save_image(image_url, str(output_path))
                
                file_size = output_path.stat().st_size / 1024
                print(f"   ✅ 保存成功: {output_path.name} ({file_size:.1f} KB)")
                print(f"   Provider: {provider}")
                
                results.append((section, str(output_path), provider))
                
            except Exception as e:
                print(f"   ❌ 生成失败: {e}")
                results.append((section, None, None))
        
        return results
    
    def insert_images_to_markdown(self, markdown_path, image_results, output_path=None):
        """
        在Markdown中插入图片
        
        Args:
            markdown_path: 原始Markdown路径
            image_results: 图片生成结果
            output_path: 输出路径（None=自动生成）
        
        Returns:
            str: 输出文件路径
        """
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        new_lines = []
        
        # 建立章节到图片的映射
        section_to_image = {}
        for section, image_path, provider in image_results:
            if image_path:
                section_to_image[section] = image_path
        
        # 插入图片
        for line in lines:
            new_lines.append(line)
            
            # 检测H2章节
            if line.startswith('## '):
                section_title = re.sub(r'^##\s*', '', line).strip()
                section_title = re.sub(r'[📍🌙⚔️💡🎯✨🎬🔥⚡️🌟💎🎨🎭🎪]', '', section_title).strip()
                
                # 如果有对应的图片，插入
                if section_title in section_to_image:
                    image_path = section_to_image[section_title]
                    # 使用相对路径
                    rel_path = Path(image_path).name
                    if Path(image_path).parent.name:
                        rel_path = f"{Path(image_path).parent.name}/{Path(image_path).name}"
                    
                    new_lines.append('')
                    new_lines.append(f'![{section_title}]({rel_path})')
                    new_lines.append('')
        
        # 生成输出路径
        if output_path is None:
            input_path = Path(markdown_path)
            output_path = input_path.parent / f"{input_path.stem}_配图版{input_path.suffix}"
        
        # 保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        return str(output_path)
    
    def illustrate(self, markdown_path, num_images=None, output_dir=None):
        """
        完整的配图流程
        
        Args:
            markdown_path: Markdown文件路径
            num_images: 配图数量（None=自动）
            output_dir: 输出目录（None=自动）
        
        Returns:
            dict: 配图报告
        """
        markdown_path = Path(markdown_path)
        
        # 分析文档
        print(f"\n📖 分析文档: {markdown_path.name}")
        doc_info = self.analyze_markdown(markdown_path)
        print(f"   标题: {doc_info['title']}")
        print(f"   章节数: {len(doc_info['sections'])}")
        
        # 生成视觉策略
        strategies = self.generate_visual_strategies(doc_info['sections'], num_images)
        print(f"   配图数: {len(strategies)}")
        
        # 确定输出目录
        if output_dir is None:
            output_dir = markdown_path.parent / f"{markdown_path.stem}_images_{self.style}"
        
        # 生成图片
        image_results = self.generate_images(strategies, output_dir)
        
        # 插入图片到Markdown
        print(f"\n📝 生成配图版Markdown...")
        output_md = self.insert_images_to_markdown(markdown_path, image_results)
        
        # 统计结果
        success_count = sum(1 for _, img, _ in image_results if img)
        
        print(f"\n{'='*60}")
        print(f"✅ 配图完成！")
        print(f"{'='*60}")
        print(f"成功: {success_count}/{len(strategies)} 张")
        print(f"图片目录: {output_dir}")
        print(f"配图版文档: {output_md}")
        print(f"{'='*60}\n")
        
        return {
            'success': success_count,
            'total': len(strategies),
            'output_md': output_md,
            'output_dir': str(output_dir),
            'results': image_results
        }


def main():
    parser = argparse.ArgumentParser(description='Markdown Illustrator - 为Markdown文档自动配图')
    
    parser.add_argument('markdown_file', help='Markdown文件路径')
    parser.add_argument('--style', '-s', default='newyorker', 
                       choices=['newyorker', 'ukiyoe'],
                       help='配图风格 (默认: newyorker)')
    parser.add_argument('--num', '-n', type=int, default=None,
                       help='配图数量 (默认: 自动)')
    parser.add_argument('--priority', '-p', default=None,
                       help='自定义provider优先级，逗号分隔，例如: modelscope,google-local,zimage')
    parser.add_argument('--output-dir', '-o', default=None,
                       help='图片输出目录 (默认: 自动生成)')
    
    args = parser.parse_args()
    
    # 解析优先级
    custom_priority = None
    if args.priority:
        custom_priority = [p.strip() for p in args.priority.split(',')]
    
    # 创建配图工具
    illustrator = MarkdownIllustrator(
        style=args.style,
        provider='auto',
        custom_priority=custom_priority
    )
    
    # 执行配图
    try:
        report = illustrator.illustrate(
            markdown_path=args.markdown_file,
            num_images=args.num,
            output_dir=args.output_dir
        )
        
        sys.exit(0 if report['success'] > 0 else 1)
        
    except Exception as e:
        print(f"\n❌ 配图失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
