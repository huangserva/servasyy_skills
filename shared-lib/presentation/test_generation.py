#!/usr/bin/env python3
"""
PPT 生成测试示例
从简单到完整的实际生成测试
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from presentation import *


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def example_1_basic_prompt():
    """示例1：生成基础 Prompt（不实际生成图片）"""
    print_section("示例 1：生成基础 Prompt")
    
    print("\n这个示例只生成 prompt，不调用图像 API")
    print("可以查看 22 种风格的 prompt 是什么样的\n")
    
    # 测试几个不同风格
    test_styles = [
        ('apple', 'soft_blue', 'cover', 'AI 技术趋势报告 2024'),
        ('blueprint', None, 'content_left', '系统架构设计'),
        ('pixel_art', None, 'cover', '像素游戏开发指南'),
        ('chalkboard', None, 'content_left', 'Python 编程入门'),
    ]
    
    for style, theme, layout, content in test_styles:
        gen = PresentationGenerator(style=style, theme=theme)
        prompt = gen.build_slide_prompt(layout=layout, content=content)
        
        print(f"\n风格: {style}" + (f" + {theme}" if theme else ""))
        print(f"布局: {layout}")
        print(f"内容: {content}")
        print(f"\n生成的 Prompt 预览（前 200 字符）:")
        print("-" * 60)
        print(prompt[:200] + "...")
        print("-" * 60)
    
    print("\n✅ 示例完成！你可以看到不同风格的 prompt 差异")


def example_2_with_session():
    """示例2：使用 Session 管理（不实际生成图片）"""
    print_section("示例 2：使用 Session 管理")
    
    print("\n这个示例展示完整的 Session 工作流")
    print("创建专业目录、保存 prompts 等\n")
    
    # 1. 创建会话
    print("1️⃣ 创建会话")
    session = create_session(
        title="微服务架构设计指南",
        style='blueprint',
        language='zh',
        audience='experts'
    )
    print(f"   Session ID: {session.session_id}")
    print(f"   Slug: {session.metadata['slug']}")
    
    # 2. 创建输出目录
    print("\n2️⃣ 创建输出目录")
    output_dir = session.create_output_directory("微服务架构设计指南")
    session.metadata['output_dir'] = str(output_dir)
    print(f"   目录: {output_dir}")
    
    # 3. 生成 prompts 并保存
    print("\n3️⃣ 生成并保存 prompts")
    
    slides = [
        ('cover', '微服务架构设计指南', '封面'),
        ('section_divider', '第一章：架构概述', '章节'),
        ('content_left', '• 服务拆分原则\n• API 网关设计\n• 数据一致性', '架构原则'),
        ('content_center', '核心概念：领域驱动设计\nDDD 在微服务中的应用', '核心概念'),
        ('content_two_column', '优势：\n• 独立部署\n• 技术多样性\n\n挑战：\n• 分布式复杂性\n• 数据一致性', '优缺点对比'),
    ]
    
    gen = PresentationGenerator(session_id=session.session_id)
    
    for i, (layout, content, title) in enumerate(slides, 1):
        prompt = gen.build_slide_prompt(layout=layout, content=content)
        session.add_prompt(i, prompt, save_to_file=True, slide_title=title)
        print(f"   ✓ 第{i}页: {title} ({layout})")
    
    # 4. 查看生成的文件
    print("\n4️⃣ 查看生成的文件结构")
    prompts_dir = output_dir / 'prompts'
    
    print(f"\n{output_dir.name}/")
    print("├── prompts/")
    for prompt_file in sorted(prompts_dir.glob('*.md')):
        print(f"│   ├── {prompt_file.name}")
    print("└── (生成的图片将在这里)")
    
    # 5. 读取一个 prompt 示例
    print("\n5️⃣ 查看保存的 prompt 内容（第1页）")
    first_prompt = list(sorted(prompts_dir.glob('*.md')))[0]
    with open(first_prompt, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"\n{first_prompt.name}:")
    print("-" * 60)
    print(content[:300] + "...")
    print("-" * 60)
    
    print(f"\n✅ 示例完成！")
    print(f"\n📁 查看完整输出: {output_dir}")
    print(f"   - 包含 {len(slides)} 个 prompt 文件")
    print(f"   - 可以手动编辑 prompts/*.md 文件后重新生成")
    
    # 不清理，让用户可以查看
    print(f"\n💡 提示：目录保留供你查看，可手动删除：")
    print(f"   rm -rf {output_dir}")


def example_3_style_comparison():
    """示例3：风格对比（生成多种风格的 prompt）"""
    print_section("示例 3：风格对比")
    
    print("\n这个示例对比不同风格对同一内容的 prompt 差异\n")
    
    # 同一内容，不同风格
    content = "人工智能的未来发展趋势"
    layout = "cover"
    
    compare_styles = [
        'apple',
        'blueprint',
        'notion',
        'chalkboard',
        'pixel_art',
        'watercolor',
    ]
    
    print(f"内容: {content}")
    print(f"布局: {layout}\n")
    
    for style in compare_styles:
        gen = PresentationGenerator(style=style)
        prompt = gen.build_slide_prompt(layout=layout, content=content)
        
        # 提取风格特征关键词
        keywords = []
        if 'APPLE' in prompt.upper():
            keywords.append('Apple 设计')
        if 'BLUEPRINT' in prompt.upper():
            keywords.append('蓝图风格')
        if 'PIXEL' in prompt.upper():
            keywords.append('像素艺术')
        if 'CHALKBOARD' in prompt.upper():
            keywords.append('黑板')
        if 'WATERCOLOR' in prompt.upper():
            keywords.append('水彩')
        if 'NOTION' in prompt.upper():
            keywords.append('SaaS 仪表盘')
        
        print(f"\n{style}:")
        print(f"  特征: {', '.join(keywords) if keywords else '标准风格'}")
        print(f"  Prompt 长度: {len(prompt)} 字符")
    
    print("\n✅ 示例完成！可以看到不同风格的特征")


def example_4_custom_style():
    """示例4：创建和使用自定义风格"""
    print_section("示例 4：自定义风格（EXTEND）")
    
    print("\n这个示例展示如何创建企业品牌风格\n")
    
    # 1. 创建自定义风格
    print("1️⃣ 创建自定义风格模板")
    custom_name = 'demo_brand'
    
    try:
        ext_file = create_custom_style(
            custom_name,
            extends='apple',
            location='user'
        )
        print(f"   创建成功: {ext_file}")
    except Exception as e:
        print(f"   创建失败: {e}")
        return
    
    # 2. 编辑自定义风格（示例）
    print("\n2️⃣ 编辑自定义风格")
    print("   你可以编辑以下内容:")
    print(f"   - 文件: {ext_file}")
    print("   - 修改品牌色: Custom Color: #YOUR_BRAND_COLOR")
    print("   - 修改字体: Custom Font: Your Brand Font")
    print("   - 添加 Logo 要求等")
    
    # 3. 使用自定义风格
    print("\n3️⃣ 使用自定义风格")
    gen = PresentationGenerator(style=custom_name)
    prompt = gen.build_slide_prompt(
        layout='cover',
        content='公司产品发布会'
    )
    
    print(f"   风格: {custom_name}")
    print(f"   继承: apple")
    print(f"   Prompt 包含自定义内容: {'CUSTOM OVERRIDE' in prompt}")
    
    # 4. 查看生成的 prompt
    print("\n4️⃣ 生成的 Prompt 预览")
    print("-" * 60)
    print(prompt[:400] + "...")
    print("-" * 60)
    
    # 清理（可选）
    print(f"\n💡 提示：自定义风格已创建")
    print(f"   - 文件: {ext_file}")
    print(f"   - 你可以编辑它来定制你的品牌风格")
    print(f"   - 使用: PresentationGenerator(style='{custom_name}')")
    
    # 是否保留
    import sys
    if '--cleanup' in sys.argv:
        ext_file.unlink()
        print(f"\n   (已删除测试扩展)")
    
    print("\n✅ 示例完成！")


def example_5_smart_recommendation():
    """示例5：智能推荐测试"""
    print_section("示例 5：智能推荐")
    
    print("\n这个示例测试智能推荐算法\n")
    
    test_cases = [
        ("技术架构", "微服务系统架构设计，包括 API 网关、服务注册、配置中心等技术组件"),
        ("游戏教程", "像素风格游戏开发入门，从零开始制作复古 8 位游戏"),
        ("教育课程", "Python 编程入门教程，面向零基础学员的手把手教学"),
        ("SaaS 产品", "我们的 SaaS 产品仪表盘，展示核心指标和业务数据"),
        ("科学研究", "生物学分子结构研究，蛋白质折叠实验报告"),
        ("生活方式", "健康养生指南，瑜伽和冥想的自然疗法"),
    ]
    
    print("测试智能推荐功能:\n")
    
    for title, content in test_cases:
        recs = recommend_styles(content, title, top_n=3, detailed=False)
        
        print(f"📌 {title}:")
        print(f"   内容: {content[:40]}...")
        print(f"   推荐 Top 3:")
        for i, r in enumerate(recs, 1):
            theme_str = f"+{r['theme']}" if r['theme'] else ""
            print(f"      {i}. {r['style']}{theme_str} ({r['confidence']:.0%}) - {r['reason']}")
        print()
    
    print("✅ 示例完成！可以看到不同内容推荐的风格")


def run_all_examples():
    """运行所有示例"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "PPT 生成测试示例" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    
    examples = [
        ("基础 Prompt 生成", example_1_basic_prompt),
        ("Session 管理工作流", example_2_with_session),
        ("风格对比", example_3_style_comparison),
        ("自定义风格（EXTEND）", example_4_custom_style),
        ("智能推荐", example_5_smart_recommendation),
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n选择示例（输入编号，或直接回车运行所有）:")
    choice = input(">>> ").strip()
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(examples):
            name, func = examples[idx]
            print(f"\n运行示例: {name}")
            func()
        else:
            print("❌ 无效的选择")
    else:
        # 运行所有示例
        for name, func in examples:
            func()
            input("\n按回车继续下一个示例...")
    
    print("\n" + "=" * 60)
    print("示例演示完成！")
    print("=" * 60)
    print("\n💡 提示:")
    print("  - 所有示例都只生成 prompt，不调用实际的图像 API")
    print("  - 你可以查看生成的 prompt 来了解不同风格")
    print("  - Session 示例会创建真实的目录和文件供你查看")
    print("  - 要实际生成图片，需要集成图像生成 API")
    print("\n查看完整文档:")
    print("  ~/.claude/skills/ppt-generator/FINAL_REPORT.md")
    print()


if __name__ == '__main__':
    import sys
    
    # 支持直接运行单个示例
    if len(sys.argv) > 1:
        example_map = {
            '1': example_1_basic_prompt,
            '2': example_2_with_session,
            '3': example_3_style_comparison,
            '4': example_4_custom_style,
            '5': example_5_smart_recommendation,
        }
        
        choice = sys.argv[1]
        if choice in example_map:
            example_map[choice]()
        else:
            print(f"❌ 未知示例: {choice}")
            print("可用: 1, 2, 3, 4, 5")
    else:
        run_all_examples()
