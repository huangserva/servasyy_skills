#!/usr/bin/env python3
"""
NotebookLM PPT 完整生成（带图片）
使用 shared-lib 的 image_api 生成实际幻灯片图片
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from presentation import *

# 导入图像生成 API
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from image_api import generate_image


def generate_notebooklm_ppt_with_images():
    """生成 NotebookLM PPT（包含图片）"""
    
    print("\n" + "=" * 60)
    print("  生成 NotebookLM PPT（完整版 - 含图片）")
    print("=" * 60)
    
    # NotebookLM 的内容描述
    content_description = """
    NotebookLM 是 Google 推出的 AI 笔记助手。
    它可以帮助用户整理笔记、提取关键信息、生成摘要。
    主要功能包括文档理解、智能问答、自动生成大纲等。
    适合学生、研究人员、知识工作者使用。
    """
    
    # Step 1: 智能推荐风格
    print("\n1️⃣ 智能推荐风格")
    
    recs = recommend_styles(
        content_description,
        title="NotebookLM 功能介绍",
        top_n=3
    )
    
    selected = recs[0]
    print(f"   选择风格: {selected['style']}")
    if selected['theme']:
        print(f"   选择主题: {selected['theme']}")
    
    # Step 2: 创建会话
    print("\n2️⃣ 创建会话和目录")
    
    session = create_session(
        title="NotebookLM 功能介绍",
        style=selected['style'],
        theme=selected.get('theme'),
        language='zh',
        audience='general'
    )
    
    output_dir = session.create_output_directory("NotebookLM 功能介绍")
    session.metadata['output_dir'] = str(output_dir)
    
    print(f"   输出目录: {output_dir}")
    
    # Step 3: 定义幻灯片内容
    print("\n3️⃣ 定义幻灯片内容（7 页）")
    
    slides = [
        {
            'layout': 'cover',
            'title': '封面',
            'content': 'NotebookLM 功能介绍\nGoogle AI 笔记助手'
        },
        {
            'layout': 'section_divider',
            'title': '什么是 NotebookLM',
            'content': '第一章：产品概述'
        },
        {
            'layout': 'content_left',
            'title': '核心功能',
            'content': '''• 智能文档理解
• AI 驱动的笔记整理
• 自动生成摘要和大纲
• 智能问答系统
• 多文档关联分析'''
        },
        {
            'layout': 'content_center',
            'title': '核心概念',
            'content': '''NotebookLM = Notebook + Language Model

将传统笔记本与大语言模型结合
打造个人知识助手'''
        },
        {
            'layout': 'content_two_column',
            'title': '优势对比',
            'content': '''优势：
• AI 自动整理
• 智能提取要点
• 多格式支持
• 隐私保护

适用场景：
• 学术研究
• 工作笔记
• 学习总结
• 知识管理'''
        },
        {
            'layout': 'content_left',
            'title': '使用方法',
            'content': '''1. 上传文档（PDF、Docs 等）
2. NotebookLM 自动分析
3. 提出问题，AI 回答
4. 生成摘要和大纲
5. 导出整理后的笔记'''
        },
        {
            'layout': 'content_center',
            'title': '总结',
            'content': '''NotebookLM 让笔记更智能
提升知识工作效率'''
        }
    ]
    
    # Step 4: 生成 prompts 和图片（多线程并行）
    print("\n4️⃣ 生成 prompts 和图片（多线程并行）")
    print("   (使用 3 个线程并行生成，大幅缩短等待时间)\n")
    
    # 先保存所有 prompts
    gen = PresentationGenerator(
        session_id=session.session_id,
        style=selected['style'],
        theme=selected.get('theme'),
        provider='google-local'  # 使用本地 Google API
    )
    
    for i, slide in enumerate(slides, 1):
        prompt = gen.build_slide_prompt(
            layout=slide['layout'],
            content=slide['content']
        )
        session.add_prompt(
            i, 
            prompt, 
            save_to_file=True, 
            slide_title=slide['title']
        )
    print(f"   ✓ 已保存 {len(slides)} 个 prompts")
    
    # 准备批量生成配置
    slides_config = [
        {
            'layout': slide['layout'],
            'content': slide['content']
        }
        for slide in slides
    ]
    
    # 使用多线程批量生成图片
    print(f"\n   ⏳ 开始多线程生成 {len(slides)} 张图片...")
    
    try:
        results = gen.batch_generate_slides(
            slides_config=slides_config,
            output_dir=str(output_dir),
            parallel=True,
            max_workers=3  # 3 个线程并行
        )
        print(f"\n   ✅ 成功生成 {len(results)} 张图片")
    except Exception as e:
        print(f"\n   ❌ 批量生成失败: {e}")
    
    # Step 5: 导出 PPTX 和 PDF
    print("\n5️⃣ 导出 PPTX 和 PDF")
    
    try:
        results = export_both(output_dir)
        
        if 'pptx' in results:
            print(f"   ✅ PPTX: {results['pptx']}")
        if 'pdf' in results:
            print(f"   ✅ PDF: {results['pdf']}")
    
    except Exception as e:
        print(f"   ⚠️  导出失败: {e}")
        print(f"   你可以手动导出:")
        print(f"   from presentation import export_both")
        print(f"   export_both(Path('{output_dir}'))")
    
    # 总结
    print("\n" + "=" * 60)
    print("✅ NotebookLM PPT 生成完成！")
    print("=" * 60)
    
    print(f"\n📁 输出目录: {output_dir}")
    print(f"   - prompts/: {len(slides)} 个 prompt 文件")
    print(f"   - slide_*.png: 幻灯片图片")
    print(f"   - presentation.pptx: PowerPoint 文件")
    print(f"   - presentation.pdf: PDF 文件")
    
    print(f"\n🔍 查看结果:")
    print(f"   open {output_dir}")
    
    return {
        'output_dir': output_dir,
        'slides_count': len(slides),
        'session_id': session.session_id
    }


if __name__ == '__main__':
    print("\n⚠️  注意：此脚本会调用图像生成 API")
    print("   - 需要配置 config.yaml")
    print("   - 每张图片可能需要 10-30 秒")
    print("   - 7 张图片预计总时间：2-5 分钟")
    
    choice = input("\n是否继续？(y/n): ").strip().lower()
    
    if choice == 'y':
        result = generate_notebooklm_ppt_with_images()
        
        print(f"\n📊 生成信息:")
        print(f"   Session: {result['session_id']}")
        print(f"   幻灯片: {result['slides_count']} 页")
        print(f"   输出: {result['output_dir']}")
    else:
        print("\n❌ 已取消")
        print("\n💡 你也可以运行不带图片的版本:")
        print("   python3 presentation/generate_notebooklm.py")
