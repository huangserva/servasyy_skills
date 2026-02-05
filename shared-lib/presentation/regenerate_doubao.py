#!/usr/bin/env python3
"""
使用 doubao-4 重新生成 NotebookLM PPT
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from presentation import *

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from image_api import generate_image


def regenerate_with_doubao():
    """使用 doubao-4 重新生成"""
    
    print("\n" + "=" * 60)
    print("  使用 doubao-4 重新生成 NotebookLM PPT")
    print("=" * 60)
    
    # 使用已有的 prompts
    prompts_dir = Path.home() / 'slide-deck/notebooklm-功能介绍-20260123-191052/prompts'
    
    if not prompts_dir.exists():
        print("❌ 未找到原 prompts 目录")
        return
    
    # 创建新目录
    print("\n1️⃣ 创建新输出目录")
    session = create_session(
        title="NotebookLM 功能介绍 (doubao-4)",
        style='apple',
        theme='soft_blue',
        language='zh'
    )
    
    output_dir = session.create_output_directory("NotebookLM-doubao4")
    print(f"   输出: {output_dir}")
    
    # 读取并生成
    print("\n2️⃣ 使用 doubao-4 重新生成图片")
    print("   (豆包 4 - 质量更好)\n")
    
    prompt_files = sorted(prompts_dir.glob('*.md'))
    
    for i, prompt_file in enumerate(prompt_files, 1):
        print(f"   第{i}页: {prompt_file.stem}")
        
        # 读取 prompt
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        # 保存到新目录
        new_prompt_file = output_dir / 'prompts' / prompt_file.name
        with open(new_prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        # 生成图片（指定使用 doubao-4）
        image_path = output_dir / f'slide_{i:02d}.png'
        
        print(f"      ⏳ 生成中...")
        
        try:
            success = generate_image(
                prompt=prompt,
                output_path=str(image_path),
                width=1920,
                height=1080,
                provider='volcengine',  # 指定使用火山引擎（doubao-4）
                max_retries=3
            )
            
            if success:
                print(f"      ✅ 完成: slide_{i:02d}.png")
            else:
                print(f"      ❌ 失败")
        
        except Exception as e:
            print(f"      ❌ 错误: {e}")
        
        print()
    
    # 导出
    print("\n3️⃣ 导出 PDF")
    try:
        from presentation import export_to_pdf
        export_to_pdf(output_dir)
        print(f"   ✅ PDF: {output_dir}/presentation.pdf")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    print("\n" + "=" * 60)
    print("✅ 完成！使用 doubao-4 重新生成")
    print("=" * 60)
    print(f"\n📁 新目录: {output_dir}")
    print(f"🔍 查看: open {output_dir}")
    
    return output_dir


if __name__ == '__main__':
    output = regenerate_with_doubao()
