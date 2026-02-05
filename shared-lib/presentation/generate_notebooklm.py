#!/usr/bin/env python3
"""
生成 NotebookLM 功能介绍 PPT
完整演示从内容分析到生成 prompts 的流程
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from presentation import *


def generate_notebooklm_ppt():
    """生成 NotebookLM 功能介绍 PPT"""
    
    print("\n" + "=" * 60)
    print("  生成 NotebookLM 功能介绍 PPT")
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
    print("   分析内容...")
    
    recs = recommend_styles(
        content_description,
        title="NotebookLM 功能介绍",
        top_n=3,
        detailed=True
    )
    
    print("\n   推荐 Top 3:")
    for i, r in enumerate(recs, 1):
        theme_str = f"+{r['theme']}" if r['theme'] else ""
        print(f"   {i}. {r['style']}{theme_str} ({r['confidence']:.0%})")
        print(f"      理由: {r['reason']}")
        if 'style_description' in r:
            print(f"      描述: {r['style_description']}")
    
    # 用户选择（这里自动选第一个）
    selected = recs[0]
    print(f"\n   ✅ 选择风格: {selected['style']}")
    if selected['theme']:
        print(f"   ✅ 选择主题: {selected['theme']}")
    
    # Step 2: 创建会话
    print("\n2️⃣ 创建会话")
    
    session = create_session(
        title="NotebookLM 功能介绍",
        style=selected['style'],
        theme=selected.get('theme'),
        language='zh',
        audience='general'
    )
    
    print(f"   Session ID: {session.session_id}")
    print(f"   Slug: {session.metadata['slug']}")
    
    # Step 3: 创建输出目录
    print("\n3️⃣ 创建输出目录")
    
    output_dir = session.create_output_directory("NotebookLM 功能介绍")
    session.metadata['output_dir'] = str(output_dir)
    
    print(f"   目录: {output_dir}")
    
    # Step 4: 定义幻灯片内容
    print("\n4️⃣ 定义幻灯片内容")
    
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
    
    print(f"   共 {len(slides)} 页幻灯片")
    for i, slide in enumerate(slides, 1):
        print(f"   {i}. {slide['title']} ({slide['layout']})")
    
    # Step 5: 生成 prompts
    print("\n5️⃣ 生成并保存 prompts")
    
    gen = PresentationGenerator(session_id=session.session_id)
    
    for i, slide in enumerate(slides, 1):
        # 生成 prompt
        prompt = gen.build_slide_prompt(
            layout=slide['layout'],
            content=slide['content']
        )
        
        # 保存 prompt
        session.add_prompt(
            i, 
            prompt, 
            save_to_file=True, 
            slide_title=slide['title']
        )
        
        print(f"   ✓ 第{i}页: {slide['title']}")
    
    # Step 6: 查看生成的文件
    print("\n6️⃣ 查看生成的文件")
    
    prompts_dir = output_dir / 'prompts'
    prompt_files = sorted(prompts_dir.glob('*.md'))
    
    print(f"\n   {output_dir.name}/")
    print(f"   ├── prompts/")
    for pf in prompt_files:
        size = pf.stat().st_size
        print(f"   │   ├── {pf.name} ({size} bytes)")
    print(f"   └── (生成的图片将保存在这里)")
    
    # Step 7: 展示第一个 prompt
    print("\n7️⃣ 查看第1页 Prompt 示例")
    
    first_prompt_file = prompt_files[0]
    with open(first_prompt_file, 'r', encoding='utf-8') as f:
        prompt_content = f.read()
    
    print(f"\n   文件: {first_prompt_file.name}")
    print("   " + "-" * 56)
    
    # 只显示前 500 字符
    preview = prompt_content[:500]
    print("   " + "\n   ".join(preview.split('\n')))
    print("   ...")
    print("   " + "-" * 56)
    
    # Step 8: 下一步指引
    print("\n8️⃣ 下一步")
    print(f"\n   ✅ Prompts 已生成并保存")
    print(f"   📁 输出目录: {output_dir}")
    print(f"   📝 Prompts 数量: {len(prompt_files)} 个")
    
    print(f"\n   要生成实际的幻灯片图片，你需要：")
    print(f"   1. 选择图像生成 API（DALL-E 3, Midjourney, Stable Diffusion 等）")
    print(f"   2. 使用保存的 prompts 生成图片")
    print(f"   3. 将图片保存为: {output_dir}/slide_01.png, slide_02.png, ...")
    print(f"   4. 运行导出：")
    print(f"      from presentation import export_both")
    print(f"      export_both(Path('{output_dir}'))")
    
    print(f"\n   💡 你也可以：")
    print(f"   - 查看并编辑 prompts/*.md 文件")
    print(f"   - 调整风格描述，重新生成")
    print(f"   - 查看 Session 元数据: ~/.claude/skills/shared-lib/presentation/.sessions/{session.session_id}.json")
    
    print(f"\n" + "=" * 60)
    print("✅ NotebookLM PPT 准备完成！")
    print("=" * 60)
    
    # 返回关键信息
    return {
        'session_id': session.session_id,
        'output_dir': output_dir,
        'style': selected['style'],
        'theme': selected.get('theme'),
        'slides_count': len(slides),
        'prompts_files': prompt_files
    }


if __name__ == '__main__':
    result = generate_notebooklm_ppt()
    
    print(f"\n📊 生成信息:")
    print(f"   Session: {result['session_id']}")
    print(f"   风格: {result['style']}")
    if result['theme']:
        print(f"   主题: {result['theme']}")
    print(f"   幻灯片: {result['slides_count']} 页")
    print(f"   输出: {result['output_dir']}")
    
    print(f"\n🔍 快速查看:")
    print(f"   ls -lh {result['output_dir']}/prompts/")
    print(f"   cat {result['prompts_files'][0]}")
