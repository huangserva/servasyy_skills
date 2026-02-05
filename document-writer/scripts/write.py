#!/usr/bin/env python3
"""
多风格文档写作工具
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# 添加共享库路径
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from writing import (
    list_styles,
    get_style_info,
    recommend_styles,
    get_style_prompt
)


def show_style_preview(content: str) -> str:
    """显示3变体预览"""
    print("\n" + "="*60)
    print("🎨 写作风格推荐（3变体预览）")
    print("="*60)
    
    recs = recommend_styles(content, top_n=3, detailed=True)
    
    for i, rec in enumerate(recs, 1):
        confidence = rec['confidence']
        stars = "★" * int(confidence * 5) + "☆" * (5 - int(confidence * 5))
        display_name = rec.get('display_name', rec['style'])
        
        print(f"\n{i}. {display_name} ({rec['style']}) {stars}")
        print(f"   推荐理由: {rec['reason']}")
        
        if 'word_count' in rec:
            wc = rec['word_count']
            print(f"   字数范围: {wc.get('min', '?')}-{wc.get('max', '?')}字")
        
        if 'best_for' in rec and rec['best_for']:
            print(f"   适用场景: {', '.join(rec['best_for'][:3])}")
    
    print("\n" + "-"*60)
    print("请选择风格 (1/2/3)，或输入风格名称:")
    
    return recs[0]['style']


def show_style_guide(style: str):
    """显示风格指南"""
    prompt = get_style_prompt(style)
    if prompt:
        print("\n" + "="*60)
        print(f"📖 {style} 风格指南")
        print("="*60)
        print(prompt)
    else:
        print(f"❌ 风格不存在: {style}")


def generate_metadata(title: str, style: str, word_count: int, source: str = None) -> dict:
    """生成元数据"""
    style_info = get_style_info(style)
    
    return {
        'title': title,
        'style': style,
        'style_display_name': style_info.get('display_name', style) if style_info else style,
        'word_count': word_count,
        'source': source,
        'created_at': datetime.now().isoformat(),
        'generator': 'document-writer'
    }


def save_output(content: str, title: str, style: str, output_dir: str = '.', source: str = None):
    """保存输出"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存Markdown
    md_file = output_path / f"{title}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Markdown: {md_file}")
    
    # 保存元数据
    word_count = len(content)
    metadata = generate_metadata(title, style, word_count, source)
    
    meta_file = output_path / "metadata.json"
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"📋 元数据: {meta_file}")
    
    return md_file


def main():
    parser = argparse.ArgumentParser(description='多风格文档写作工具')
    parser.add_argument('input', nargs='?', help='主题或素材文件路径')
    parser.add_argument('--style', '-s', help='写作风格')
    parser.add_argument('--output', '-o', default='.', help='输出目录')
    parser.add_argument('--preview', action='store_true', help='只显示风格预览')
    parser.add_argument('--list-styles', action='store_true', help='列出所有风格')
    parser.add_argument('--show-style', help='显示指定风格的详细指南')
    parser.add_argument('--convert', help='将现有文章转换为指定风格')
    
    args = parser.parse_args()
    
    # 列出风格
    if args.list_styles:
        print("可用写作风格:")
        for style in list_styles():
            info = get_style_info(style)
            if info:
                display_name = info.get('display_name', style)
                desc = info.get('description', '')[:50]
                wc = info.get('word_count', {})
                word_range = f"{wc.get('min', '?')}-{wc.get('max', '?')}字"
                print(f"  {style:15} {display_name:15} {word_range:15} {desc}...")
        return
    
    # 显示风格指南
    if args.show_style:
        show_style_guide(args.show_style)
        return
    
    # 需要输入
    if not args.input:
        parser.error("需要指定主题或素材文件")
    
    # 读取输入
    input_path = Path(args.input)
    if input_path.exists():
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        source = str(input_path)
    else:
        content = args.input
        source = None
    
    # 预览模式
    if args.preview:
        show_style_preview(content)
        return
    
    # 风格选择
    if args.style:
        style = args.style
    else:
        style = show_style_preview(content)
    
    # 验证风格
    if style not in list_styles():
        print(f"❌ 风格不存在: {style}")
        print(f"可用风格: {list_styles()}")
        return
    
    # 显示风格信息
    info = get_style_info(style)
    if info:
        print(f"\n📝 使用风格: {info.get('display_name', style)}")
        wc = info.get('word_count', {})
        print(f"   目标字数: {wc.get('min', '?')}-{wc.get('max', '?')}字")
    
    # 获取风格提示词
    style_prompt = get_style_prompt(style)
    
    print("\n" + "="*60)
    print("💡 请使用以下风格指南写作：")
    print("="*60)
    print(style_prompt[:1000] + "...\n")
    
    print("="*60)
    print("📌 写作任务")
    print("="*60)
    print(f"主题/素材: {content[:200]}...")
    print(f"风格: {style}")
    print(f"输出目录: {args.output}")
    print("\n请根据上述风格指南，生成文章内容。")


if __name__ == '__main__':
    main()
