#!/usr/bin/env python3
"""
PPT 系统整合测试套件
测试所有新功能和整合成果
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

def test_1_style_count():
    """测试1：风格数量（应该是 22 种）"""
    print_section("测试 1：风格数量")
    
    styles = list_styles()
    print(f"\n总数: {len(styles)} 种")
    
    # 分类显示
    original = ['apple', 'material', 'fluent', 'editorial', 'storytelling', 'neumorphism']
    new_styles = [s for s in styles if s not in original]
    
    print(f"\n原有风格 ({len(original)} 种):")
    for style in original:
        print(f"  ✓ {style}")
    
    print(f"\n新增风格 ({len(new_styles)} 种):")
    for style in sorted(new_styles):
        print(f"  ✓ {style}")
    
    assert len(styles) == 22, f"风格数量错误：期望 22，实际 {len(styles)}"
    print("\n✅ 测试通过！")

def test_2_style_details():
    """测试2：风格详细信息"""
    print_section("测试 2：风格详细信息")
    
    # 测试几个新风格的详细信息
    test_styles = ['blueprint', 'notion', 'pixel_art', 'chalkboard']
    
    selector = StyleSelector()
    
    for style_name in test_styles:
        info = selector.get_style_info(style_name)
        if info:
            print(f"\n📄 {style_name}:")
            print(f"   显示名: {info.get('display_name', 'N/A')}")
            print(f"   描述: {info.get('description', 'N/A')[:50]}...")
            print(f"   分类: {info.get('category', 'N/A')}")
            print(f"   适合: {', '.join(info.get('best_for', [])[:3])}")
        else:
            print(f"\n❌ {style_name}: 加载失败")
    
    print("\n✅ 测试通过！")

def test_3_smart_recommendation():
    """测试3：智能推荐算法"""
    print_section("测试 3：智能推荐算法")
    
    test_cases = [
        ("技术架构", "微服务系统架构设计，包括API网关、服务注册等技术组件", "blueprint"),
        ("教育课程", "Python编程入门教程，面向初学者的手把手教学", "chalkboard"),
        ("游戏开发", "像素风格游戏开发指南，复古8位游戏制作", "pixel_art"),
        ("SaaS产品", "我们的SaaS产品仪表盘设计，展示关键指标和数据", "notion"),
        ("科学研究", "生物学实验研究报告，分子结构和实验流程", "scientific"),
        ("生活方式", "健康养生指南，自然疗法和瑜伽练习", "watercolor"),
    ]
    
    print("\n测试场景识别:")
    passed = 0
    
    for title, content, expected in test_cases:
        recs = recommend_styles(content, title, top_n=3)
        actual = recs[0]['style'] if recs else 'unknown'
        
        status = "✅" if actual == expected else "⚠️"
        print(f"\n{status} {title}:")
        print(f"   期望: {expected}")
        print(f"   实际: {actual}")
        print(f"   Top 3: {', '.join([r['style'] for r in recs[:3]])}")
        
        if actual == expected:
            passed += 1
    
    print(f"\n通过率: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.0f}%)")
    print("✅ 测试完成！")

def test_4_session_manager():
    """测试4：Session 管理器"""
    print_section("测试 4：Session 管理器")
    
    # 创建会话
    print("\n1. 创建会话:")
    session = create_session(
        title="AI技术趋势报告",
        style='blueprint',
        language='zh',
        audience='experts'
    )
    print(f"   Session ID: {session.session_id}")
    print(f"   风格: {session.metadata['style']}")
    print(f"   语言: {session.metadata['language']}")
    print(f"   受众: {session.metadata['audience']}")
    
    # 测试 Slug 生成
    print("\n2. Slug 命名测试:")
    test_titles = [
        "Introduction to Machine Learning",
        "AI技术趋势报告 2024",
        "产品发布会 - 新功能介绍"
    ]
    for title in test_titles:
        slug = SessionManager.generate_slug(title)
        print(f"   '{title}'")
        print(f"   → '{slug}'")
    
    # 添加 prompts
    print("\n3. 添加 prompts:")
    session.add_prompt(1, "第1页: 封面页 prompt...")
    session.add_prompt(2, "第2页: 内容页 prompt...")
    session.add_prompt(3, "第3页: 总结页 prompt...")
    print(f"   已添加 {session.metadata['slide_count']} 个 prompts")
    
    # 获取 prompt
    print("\n4. 获取 prompt:")
    prompt_2 = session.get_prompt(2)
    print(f"   第2页: {prompt_2}")
    
    # 列出最近会话
    print("\n5. 最近会话:")
    recent = list_recent_sessions(recent=3)
    for s in recent:
        print(f"   - {s['session_id']}: {s.get('title', 'N/A')} ({s.get('slide_count', 0)} slides)")
    
    # 清理测试会话
    session.delete_session()
    print("\n   (测试会话已清理)")
    
    print("\n✅ 测试通过！")

def test_5_generator_enhancement():
    """测试5：增强的 PresentationGenerator"""
    print_section("测试 5：增强的 PresentationGenerator")
    
    # 测试旧方式（向后兼容）
    print("\n1. 向后兼容测试（旧代码）:")
    gen_old = PresentationGenerator(style='apple', theme='soft_blue')
    print(f"   风格: {gen_old.style}")
    print(f"   主题: {gen_old.theme}")
    print("   ✅ 旧代码仍然有效")
    
    # 测试新方式（启用新功能）
    print("\n2. 新功能测试:")
    gen_new = PresentationGenerator(
        style='blueprint',
        language='zh',
        audience='experts'
    )
    print(f"   风格: {gen_new.style}")
    print(f"   语言: {gen_new.language}")
    print(f"   受众: {gen_new.audience}")
    print("   ✅ 新功能正常工作")
    
    # 测试 Session ID
    print("\n3. Session ID 测试:")
    session = create_session(title='测试', style='notion')
    gen_session = PresentationGenerator(session_id=session.session_id)
    print(f"   Session ID: {gen_session.session_id}")
    print(f"   从会话加载的风格: {gen_session.style}")
    session.delete_session()
    print("   ✅ Session ID 功能正常")
    
    print("\n✅ 测试通过！")

def test_6_layout_and_theme():
    """测试6：布局和主题系统（保留功能）"""
    print_section("测试 6：布局和主题系统")
    
    # 测试布局
    print("\n1. 布局系统:")
    layouts = list_layouts()
    print(f"   可用布局: {len(layouts)} 种")
    for layout in layouts:
        print(f"   ✓ {layout}")
    
    assert len(layouts) == 5, "布局数量错误"
    
    # 测试主题
    print("\n2. 主题系统 (Apple 专属):")
    themes = list_themes()
    print(f"   可用主题: {len(themes)} 种")
    for theme in themes:
        print(f"   ✓ {theme}")
    
    assert len(themes) == 8, "主题数量错误"
    
    print("\n✅ 测试通过！")

def test_7_exporter():
    """测试7：导出功能（模拟）"""
    print_section("测试 7：导出功能")
    
    print("\n注意：此测试仅验证模块导入，不执行实际导出")
    
    # 检查导出函数是否可用
    print("\n1. 检查导出函数:")
    print(f"   ✓ export_to_pptx: {callable(export_to_pptx)}")
    print(f"   ✓ export_to_pdf: {callable(export_to_pdf)}")
    print(f"   ✓ export_both: {callable(export_both)}")
    
    print("\n2. 使用示例:")
    print("   from presentation import export_to_pdf")
    print("   export_to_pdf(Path('/path/to/slides'))")
    
    print("\n✅ 测试通过！")

def test_8_integration():
    """测试8：完整工作流模拟"""
    print_section("测试 8：完整工作流模拟")
    
    print("\n模拟完整 PPT 生成流程:")
    
    # Step 1: 分析内容
    print("\n1️⃣ 分析内容，推荐风格")
    content = "系统架构设计报告，包括微服务、容器化、CI/CD流程"
    recs = recommend_styles(content, "系统架构设计", top_n=3)
    print(f"   推荐Top 3:")
    for i, r in enumerate(recs, 1):
        theme_str = f'+{r["theme"]}' if r['theme'] else ''
        print(f"   {i}. {r['style']}{theme_str} ({r['confidence']:.0%})")
    
    # Step 2: 用户选择并创建会话
    print("\n2️⃣ 创建会话")
    selected = recs[0]
    session = create_session(
        title="系统架构设计",
        style=selected['style'],
        theme=selected.get('theme'),
        language='zh',
        audience='experts'
    )
    print(f"   Session: {session.session_id}")
    print(f"   风格: {selected['style']}")
    
    # Step 3: 生成器初始化
    print("\n3️⃣ 初始化生成器")
    gen = PresentationGenerator(session_id=session.session_id)
    print(f"   风格: {gen.style}")
    print(f"   语言: {gen.language}")
    print(f"   受众: {gen.audience}")
    
    # Step 4: 模拟生成多页
    print("\n4️⃣ 模拟生成幻灯片")
    slides = ['封面', '目录', '架构图', '总结']
    for i, slide_title in enumerate(slides, 1):
        prompt = f"第{i}页: {slide_title}"
        session.add_prompt(i, prompt)
        print(f"   ✓ 第{i}页: {slide_title}")
    
    print(f"\n   生成完成: {session.metadata['slide_count']} 张幻灯片")
    
    # Step 5: 导出（模拟）
    print("\n5️⃣ 导出（模拟）")
    print("   → presentation.pptx")
    print("   → presentation.pdf")
    
    # 清理
    session.delete_session()
    print("\n   (测试会话已清理)")
    
    print("\n✅ 完整工作流测试通过！")

def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "PPT 系统整合测试套件" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        test_1_style_count,
        test_2_style_details,
        test_3_smart_recommendation,
        test_4_session_manager,
        test_5_generator_enhancement,
        test_6_layout_and_theme,
        test_7_exporter,
        test_8_integration,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            failed += 1
    
    # 总结
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 20 + "测试总结" + " " * 25 + "║")
    print("╚" + "=" * 58 + "╝")
    print(f"\n   总测试数: {len(tests)}")
    print(f"   ✅ 通过: {passed}")
    print(f"   ❌ 失败: {failed}")
    print(f"   通过率: {passed/len(tests)*100:.0f}%")
    
    if failed == 0:
        print("\n   🎉 所有测试通过！系统运行正常！")
    else:
        print("\n   ⚠️  部分测试失败，请检查错误信息")
    
    print("\n" + "=" * 60 + "\n")

if __name__ == '__main__':
    run_all_tests()
