#!/usr/bin/env python3
"""
统一配图生成脚本
支持：文章配图、封面生成、单图修改/添加/删除、3变体预览
"""
import json
import re
import sys
import hashlib
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加共享库路径
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from illustration import (
    IllustrationGenerator,
    recommend_styles,
    analyze_article,
    generate_config,
    list_styles,
    list_layouts
)
from image_api import ImageGenerator


def get_cache_key(visual_desc, caption=''):
    """生成缓存键"""
    content = f"{visual_desc}|{caption}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]


def check_cache(cache_dir, cache_key):
    """检查缓存"""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{cache_key}.png"
    return str(cache_file) if cache_file.exists() else None


def save_to_cache(cache_dir, cache_key, image_path):
    """保存到缓存"""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{cache_key}.png"
    if Path(image_path).exists():
        import shutil
        shutil.copy2(image_path, cache_file)


def insert_image_into_markdown(markdown_path, h2_title, image_path):
    """在H2标题后插入图片引用"""
    with open(markdown_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if re.match(rf'^##\s+{re.escape(h2_title)}\s*$', line.strip()):
            for j in range(1, 6):
                if i + j >= len(lines):
                    break
                check_line = lines[i + j].strip()
                if check_line.startswith('#'):
                    break
                if check_line.startswith('![') and image_path in check_line:
                    return

            image_md = f"\n![{h2_title}]({image_path})\n\n"
            lines.insert(i + 1, image_md)

            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return


def generate_single_image(args):
    """生成单张图片（用于并行处理）"""
    (idx, section, abs_output_dir, output_dir, markdown_path, 
     ill_gen, style, skip_existing, cache_dir) = args
    
    h2_title = section['h2_title']
    visual_desc = section['visual_description']
    layout = section.get('layout', 'single')
    caption = section.get('caption', '')
    
    if visual_desc == "待Claude分析填写..." or not visual_desc.strip():
        return {'success': False, 'idx': idx, 'reason': '未填写visual_description'}
    
    image_filename = f"illustration_{idx:02d}.png"
    image_output_path = abs_output_dir / image_filename
    image_rel_path = f"{output_dir}/{image_filename}"
    
    # 检查是否已存在
    if skip_existing and image_output_path.exists():
        insert_image_into_markdown(markdown_path, h2_title, image_rel_path)
        return {'success': True, 'idx': idx, 'cached': True, 'title': h2_title}
    
    # 检查缓存
    cache_key = get_cache_key(visual_desc, caption)
    cached_path = check_cache(cache_dir, cache_key)
    if cached_path:
        import shutil
        shutil.copy2(cached_path, image_output_path)
        insert_image_into_markdown(markdown_path, h2_title, image_rel_path)
        return {'success': True, 'idx': idx, 'cached': True, 'title': h2_title, 'from_cache': True}
    
    try:
        # 使用 IllustrationGenerator 生成
        image_url, used_provider = ill_gen.generate(
            content=visual_desc,
            style=style,
            layout=layout,
            aspect_ratio='16:9',
            output_path=str(image_output_path)
        )
        
        save_to_cache(cache_dir, cache_key, image_output_path)
        insert_image_into_markdown(markdown_path, h2_title, image_rel_path)
        
        return {
            'success': True, 
            'idx': idx, 
            'title': h2_title, 
            'provider': used_provider,
            'cached': False
        }
        
    except Exception as e:
        return {'success': False, 'idx': idx, 'title': h2_title, 'error': str(e)}


def show_style_preview(content: str) -> str:
    """显示3变体预览，让用户选择"""
    print("\n" + "="*60)
    print("🎨 风格推荐（3变体预览）")
    print("="*60)
    
    recs = recommend_styles(content, top_n=3, detailed=True)
    
    for i, rec in enumerate(recs, 1):
        confidence = rec['confidence']
        stars = "★" * int(confidence * 5) + "☆" * (5 - int(confidence * 5))
        print(f"\n{i}. {rec['style']} {stars}")
        print(f"   推荐理由: {rec['reason']}")
        print(f"   默认布局: {rec['layout']}")
        if 'style_description' in rec:
            print(f"   风格描述: {rec['style_description'][:50]}...")
    
    print("\n" + "-"*60)
    print("请选择风格 (1/2/3)，或输入风格名称:")
    
    # 返回第一个推荐作为默认
    return recs[0]['style']


def generate_from_config(
    markdown_path,
    config_path="visual_config.json",
    output_dir="images/illustrations",
    style=None,
    skip_existing=True,
    max_workers=4,
    cover_only=False
):
    """并行生成所有配图"""
    markdown_path = Path(markdown_path)
    config_file = markdown_path.parent / config_path

    # 如果配置不存在，自动生成
    if not config_file.exists():
        print("📝 配置文件不存在，自动分析文章...")
        analysis = analyze_article(str(markdown_path))
        
        # 显示分析结果
        print(f"\n📖 文章: {analysis['title']}")
        print(f"📊 识别到 {len(analysis['illustrations'])} 个章节需要配图")
        
        # 如果没有指定风格，显示3变体预览
        if not style:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            default_style = show_style_preview(content)
            style = default_style
        
        # 生成配置
        generate_config(str(markdown_path), style=style)
    
    # 读取配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    style = style or config.get('style', 'newyorker')
    sections = config.get('sections', [])
    
    print(f"\n📋 配置: {len(sections)} 个章节, 风格: {style}")
    print(f"⚡ 并行线程数: {max_workers}")

    abs_output_dir = markdown_path.parent / output_dir
    abs_output_dir.mkdir(parents=True, exist_ok=True)
    
    cache_dir = markdown_path.parent / '.illustration_cache'
    cache_dir.mkdir(parents=True, exist_ok=True)

    ill_gen = IllustrationGenerator()

    # 生成封面图
    cover_config = config.get('cover', {})
    cover_desc = cover_config.get('visual_description', '')
    if cover_desc:
        cover_path = abs_output_dir / "cover.png"
        if not (skip_existing and cover_path.exists()):
            print(f"\n📖 生成封面图...")
            try:
                image_url, used_provider = ill_gen.generate(
                    content=cover_desc,
                    style=style,
                    layout='single',
                    aspect_ratio='3:4',
                    output_path=str(cover_path)
                )
                print(f"   ✅ 封面已保存 ({used_provider})")
            except Exception as e:
                print(f"   ❌ 封面生成失败: {e}")
    
    if cover_only:
        print("\n✨ 封面生成完成！")
        return 1

    # 并行生成章节配图
    print(f"\n🚀 开始并行生成 {len(sections)} 张配图...")
    
    tasks = [
        (idx, section, abs_output_dir, output_dir, markdown_path, 
         ill_gen, style, skip_existing, cache_dir)
        for idx, section in enumerate(sections, 1)
    ]
    
    success_count = 0
    cached_count = 0
    failed_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(generate_single_image, task): task[0] for task in tasks}
        
        for future in as_completed(futures):
            result = future.result()
            idx = result['idx']
            
            if result['success']:
                success_count += 1
                if result.get('cached'):
                    cached_count += 1
                    status = "缓存" if result.get('from_cache') else "已存在"
                    print(f"✅ [{idx}/{len(sections)}] {result['title']} - {status}")
                else:
                    provider = result.get('provider', 'unknown')
                    print(f"✅ [{idx}/{len(sections)}] {result['title']} - 新生成 ({provider})")
            else:
                failed_count += 1
                reason = result.get('reason') or result.get('error', 'unknown')
                title = result.get('title', f'章节{idx}')
                print(f"❌ [{idx}/{len(sections)}] {title} - 失败: {reason}")

    print("\n" + "="*60)
    print(f"✨ 完成！成功: {success_count}/{len(sections)}, 缓存: {cached_count}, 失败: {failed_count}")
    print(f"📁 图片: {output_dir}")
    print(f"💾 缓存: .illustration_cache")

    return success_count


def regenerate_image(markdown_path, image_name, new_style=None, new_content=None):
    """重新生成单张图片"""
    markdown_path = Path(markdown_path)
    work_dir = markdown_path.parent
    
    ill_gen = IllustrationGenerator()
    
    print(f"\n🔄 重新生成: {image_name}")
    if new_style:
        print(f"   新风格: {new_style}")
    
    try:
        image_url, provider = ill_gen.regenerate_illustration(
            work_dir=str(work_dir),
            image_name=image_name,
            new_content=new_content,
            new_style=new_style
        )
        print(f"✅ 重新生成完成 ({provider})")
        return True
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return False


def add_image(markdown_path, position, content, style=None, layout='single'):
    """添加新配图"""
    markdown_path = Path(markdown_path)
    work_dir = markdown_path.parent
    
    ill_gen = IllustrationGenerator()
    
    print(f"\n➕ 添加配图: 位置 {position}")
    print(f"   内容: {content[:50]}...")
    
    try:
        image_url, provider = ill_gen.add_illustration(
            work_dir=str(work_dir),
            position=position,
            content=content,
            style=style,
            layout=layout
        )
        print(f"✅ 添加完成 ({provider})")
        return True
    except Exception as e:
        print(f"❌ 添加失败: {e}")
        return False


def remove_image(markdown_path, image_name):
    """删除配图"""
    markdown_path = Path(markdown_path)
    work_dir = markdown_path.parent
    
    ill_gen = IllustrationGenerator()
    
    success = ill_gen.remove_illustration(str(work_dir), image_name)
    return success


def main():
    parser = argparse.ArgumentParser(description='统一配图生成器')
    parser.add_argument('markdown', nargs='?', help='Markdown文件路径')
    parser.add_argument('--config', default='visual_config.json', help='配置文件')
    parser.add_argument('--output-dir', default='images/illustrations', help='输出目录')
    parser.add_argument('--style', help='视觉风格')
    parser.add_argument('--no-skip', action='store_true', help='重新生成已存在的图片')
    parser.add_argument('--workers', type=int, default=4, help='并行线程数')
    
    # 特殊操作
    parser.add_argument('--cover-only', action='store_true', help='只生成封面')
    parser.add_argument('--regenerate', help='重新生成指定图片 (如 illustration_03.png)')
    parser.add_argument('--add', help='添加新配图，指定内容描述')
    parser.add_argument('--add-position', type=int, default=1, help='添加位置')
    parser.add_argument('--add-layout', default='single', help='添加图片的布局')
    parser.add_argument('--remove', help='删除指定图片')
    
    # 信息
    parser.add_argument('--list-styles', action='store_true', help='列出所有风格')
    parser.add_argument('--list-layouts', action='store_true', help='列出所有布局')
    parser.add_argument('--preview', action='store_true', help='只显示3变体预览，不生成')
    
    args = parser.parse_args()
    
    # 显示信息（不需要 markdown 参数）
    if args.list_styles:
        print("可用风格:", list_styles())
        return
    
    if args.list_layouts:
        print("可用布局:", list_layouts())
        return
    
    # 以下操作需要 markdown 参数
    if not args.markdown:
        parser.error("需要指定 Markdown 文件路径")
    
    # 预览模式
    if args.preview:
        with open(args.markdown, 'r', encoding='utf-8') as f:
            content = f.read()
        show_style_preview(content)
        return
    
    # 单图操作
    if args.regenerate:
        regenerate_image(args.markdown, args.regenerate, new_style=args.style)
        return
    
    if args.add:
        add_image(
            args.markdown, 
            args.add_position, 
            args.add, 
            style=args.style,
            layout=args.add_layout
        )
        return
    
    if args.remove:
        remove_image(args.markdown, args.remove)
        return
    
    # 批量生成
    generate_from_config(
        markdown_path=args.markdown,
        config_path=args.config,
        output_dir=args.output_dir,
        style=args.style,
        skip_existing=not args.no_skip,
        max_workers=args.workers,
        cover_only=args.cover_only
    )


if __name__ == '__main__':
    main()
