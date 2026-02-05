#!/usr/bin/env python3
"""
直接根据提示词生成图片

使用方式:
    python3 generate_image.py <prompt> [options]

示例:
    # 基础用法
    python3 generate_image.py "A golden cat sitting on a book"
    
    # 指定风格
    python3 generate_image.py "A warrior in battle" --style newyorker
    
    # 自定义provider
    python3 generate_image.py "A sunset scene" --provider modelscope
    
    # 自定义优先级
    python3 generate_image.py "A modern city" --priority modelscope,google-local
    
    # 指定输出文件
    python3 generate_image.py "A beautiful landscape" -o landscape.jpg
"""

import sys
import os
import argparse
from pathlib import Path

# 添加shared-lib到路径
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from image_api import ImageGenerator


def generate_image_from_prompt(
    prompt,
    style='newyorker',
    provider='auto',
    custom_priority=None,
    output_path=None,
    aspect_ratio='16:9'
):
    """
    根据提示词生成图片
    
    Args:
        prompt: 提示词（英文）
        style: 风格 ('newyorker', 'ukiyoe', 'raw')
        provider: Provider选择
        custom_priority: 自定义优先级
        output_path: 输出路径
        aspect_ratio: 宽高比
    
    Returns:
        str: 生成的图片路径
    """
    print("=" * 60)
    print("🎨 根据提示词生成图片")
    print("=" * 60)
    print(f"\n📝 提示词: {prompt}")
    print(f"🎭 风格: {style}")
    
    if custom_priority:
        print(f"🎯 自定义优先级: {custom_priority}")
    else:
        print(f"🤖 Provider: {provider}")
    
    print(f"\n{'─'*60}\n")
    
    # 创建生成器
    generator = ImageGenerator(provider=provider, custom_priority=custom_priority)
    
    try:
        # 根据风格生成
        if style == 'newyorker':
            image_url, used_provider = generator.generate_newyorker_style(
                visual_strategy=prompt,
                caption='',
                aspect_ratio=aspect_ratio,
                max_retries=1
            )
        elif style == 'ukiyoe':
            image_url, used_provider = generator.generate_ukiyoe_style(
                visual_strategy=prompt,
                caption='',
                aspect_ratio=aspect_ratio,
                max_retries=1
            )
        elif style == 'raw':
            # 原始模式：直接使用prompt，不添加风格描述
            image_url, used_provider = generator.generate_raw_style(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                max_retries=1
            )
        else:
            raise ValueError(f"不支持的风格: {style}")
        
        print(f"\n✅ 生成成功！")
        print(f"   Provider: {used_provider}")
        
        # 确定输出路径
        if output_path is None:
            timestamp = __import__('time').strftime('%Y%m%d_%H%M%S')
            output_path = f"generated_{timestamp}.jpg"
        
        # 保存图片
        generator.save_image(image_url, output_path)
        
        file_size = Path(output_path).stat().st_size / 1024
        
        print(f"\n{'='*60}")
        print(f"💾 图片已保存")
        print(f"{'='*60}")
        print(f"文件: {output_path}")
        print(f"大小: {file_size:.1f} KB")
        print(f"Provider: {used_provider}")
        print(f"{'='*60}\n")
        
        return output_path
        
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(
        description='根据提示词直接生成图片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础用法
  python3 generate_image.py "A golden cat sitting on a book"
  
  # 指定纽约客风格
  python3 generate_image.py "A warrior in battle" --style newyorker
  
  # 指定浮世绘风格
  python3 generate_image.py "Mount Fuji at sunset" --style ukiyoe
  
  # 使用ModelScope provider
  python3 generate_image.py "A modern city skyline" --provider modelscope
  
  # 自定义优先级
  python3 generate_image.py "A beautiful landscape" \\
      --priority modelscope,google-local,zimage
  
  # 指定输出文件名
  python3 generate_image.py "A starry night" -o starry_night.jpg
  
  # 指定宽高比
  python3 generate_image.py "A portrait" --aspect-ratio 9:16
        """
    )
    
    parser.add_argument('prompt', help='图片生成提示词（英文）')
    parser.add_argument('--style', '-s', default='newyorker',
                       choices=['newyorker', 'ukiyoe', 'raw'],
                       help='图片风格 (默认: newyorker)')
    parser.add_argument('--provider', '-p', default='auto',
                       choices=['auto', 'google-local', 'modelscope', 'zimage', 'volcengine', 'apimart'],
                       help='指定provider (默认: auto)')
    parser.add_argument('--priority', default=None,
                       help='自定义provider优先级，逗号分隔')
    parser.add_argument('--output', '-o', default=None,
                       help='输出文件路径 (默认: generated_<timestamp>.jpg)')
    parser.add_argument('--aspect-ratio', '-a', default='16:9',
                       choices=['16:9', '9:16', '1:1', '4:3', '3:4', '21:9'],
                       help='宽高比 (默认: 16:9)')
    
    args = parser.parse_args()
    
    # 解析优先级
    custom_priority = None
    if args.priority:
        custom_priority = [p.strip() for p in args.priority.split(',')]
    
    # 生成图片
    result = generate_image_from_prompt(
        prompt=args.prompt,
        style=args.style,
        provider=args.provider,
        custom_priority=custom_priority,
        output_path=args.output,
        aspect_ratio=args.aspect_ratio
    )
    
    sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()
