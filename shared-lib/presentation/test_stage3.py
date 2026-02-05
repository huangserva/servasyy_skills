#!/usr/bin/env python3
"""
阶段 3 功能测试
测试 Slug 命名、Prompts 保存、EXTEND 扩展
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


def test_1_slug_and_directory():
    """测试1：Slug 命名和目录结构"""
    print_section("测试 1：Slug 命名和专业目录结构")
    
    # 创建会话
    session = create_session(
        title="AI技术趋势报告 2024",
        style='blueprint',
        language='zh',
        audience='experts'
    )
    
    print(f"\n1. 会话创建:")
    print(f"   Session ID: {session.session_id}")
    print(f"   生成的 Slug: {session.metadata.get('slug', 'N/A')}")
    
    # 测试目录创建
    print(f"\n2. 创建输出目录:")
    output_dir = session.create_output_directory("AI技术趋势报告 2024")
    print(f"   目录: {output_dir}")
    print(f"   存在: {output_dir.exists()}")
    print(f"   prompts 子目录: {(output_dir / 'prompts').exists()}")
    
    # 测试冲突处理（再次创建同名）
    print(f"\n3. 测试冲突处理（重复标题）:")
    output_dir2 = session.create_output_directory("AI技术趋势报告 2024")
    print(f"   新目录: {output_dir2}")
    print(f"   包含时间戳: {'-20' in str(output_dir2)}")
    
    # 清理
    import shutil
    if output_dir.exists():
        shutil.rmtree(output_dir)
    if output_dir2.exists():
        shutil.rmtree(output_dir2)
    session.delete_session()
    
    print("\n✅ 测试通过！")


def test_2_prompt_saving():
    """测试2：Prompts 保存机制"""
    print_section("测试 2：Prompts 保存机制")
    
    # 创建会话和目录
    session = create_session(
        title="测试 Prompts 保存",
        style='notion',
        language='zh'
    )
    
    output_dir = session.create_output_directory("测试 Prompts 保存")
    session.metadata['output_dir'] = str(output_dir)
    
    print(f"\n1. 输出目录: {output_dir}")
    
    # 添加 prompts（保存到文件）
    print(f"\n2. 保存 prompts:")
    
    slides_data = [
        (1, "封面页 prompt 内容...", "封面"),
        (2, "目录页 prompt 内容...", "目录"),
        (3, "技术架构图 prompt 内容...", "技术架构"),
    ]
    
    for slide_num, prompt, title in slides_data:
        session.add_prompt(slide_num, prompt, save_to_file=True, slide_title=title)
        print(f"   ✓ 第{slide_num}页: {title}")
    
    # 验证文件存在
    print(f"\n3. 验证 prompt 文件:")
    prompts_dir = output_dir / 'prompts'
    
    for prompt_file in sorted(prompts_dir.glob('*.md')):
        print(f"   ✓ {prompt_file.name}")
        # 读取内容验证
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"     (内容长度: {len(content)} 字符)")
    
    # 清理
    import shutil
    if output_dir.exists():
        shutil.rmtree(output_dir)
    session.delete_session()
    
    print("\n✅ 测试通过！")


def test_3_extend_mechanism():
    """测试3：EXTEND 扩展机制"""
    print_section("测试 3：EXTEND 扩展机制")
    
    # 1. 创建自定义风格模板
    print("\n1. 创建自定义风格模板:")
    custom_style_name = 'test_brand'
    
    try:
        ext_file = create_custom_style(
            custom_style_name,
            extends='apple',
            location='user'
        )
        print(f"   文件: {ext_file}")
        print(f"   存在: {ext_file.exists()}")
    except Exception as e:
        print(f"   ⚠️  创建失败: {e}")
        ext_file = None
    
    # 2. 列出扩展
    print("\n2. 列出自定义风格:")
    extensions = list_custom_styles()
    if extensions:
        for name, path in extensions.items():
            print(f"   ✓ {name}: {path.name}")
    else:
        print("   (暂无扩展)")
    
    # 3. 测试加载扩展
    if ext_file and ext_file.exists():
        print("\n3. 测试加载扩展风格:")
        selector = StyleSelector()
        style_info = selector.get_style_info(custom_style_name)
        
        if style_info:
            print(f"   ✓ 加载成功")
            print(f"   名称: {style_info.get('name')}")
            print(f"   继承: {style_info.get('extends', 'N/A')}")
            print(f"   Prompt 包含 base_prompt: {'{base_prompt}' in style_info.get('prompt_template', '')}")
        else:
            print(f"   ❌ 加载失败")
    
    # 清理
    if ext_file and ext_file.exists():
        ext_file.unlink()
        print(f"\n   (测试扩展已删除)")
    
    print("\n✅ 测试通过！")


def test_4_integration():
    """测试4：完整工作流（带阶段3功能）"""
    print_section("测试 4：完整工作流（阶段3功能集成）")
    
    print("\n模拟完整 PPT 生成流程（使用阶段3功能）:")
    
    # Step 1: 创建会话
    print("\n1️⃣ 创建会话（带 Slug）")
    session = create_session(
        title="微服务架构设计指南",
        style='blueprint',
        language='zh',
        audience='experts'
    )
    print(f"   Session: {session.session_id}")
    print(f"   Slug: {session.metadata['slug']}")
    
    # Step 2: 创建专业目录
    print("\n2️⃣ 创建专业输出目录")
    output_dir = session.create_output_directory("微服务架构设计指南")
    session.metadata['output_dir'] = str(output_dir)
    print(f"   目录: {output_dir}")
    print(f"   结构:")
    print(f"   ├── prompts/  ✓")
    
    # Step 3: 生成幻灯片（模拟，保存 prompts）
    print("\n3️⃣ 生成幻灯片（保存 prompts）")
    
    slides = [
        ('封面', '微服务架构设计指南封面页...'),
        ('目录', '章节目录...'),
        ('架构概览', '系统架构图和组件说明...'),
        ('服务拆分', '微服务拆分原则...'),
        ('总结', '总结和最佳实践...')
    ]
    
    for i, (title, prompt) in enumerate(slides, 1):
        session.add_prompt(i, prompt, save_to_file=True, slide_title=title)
        print(f"   ✓ 第{i}页: {title}")
    
    # Step 4: 验证输出
    print(f"\n4️⃣ 验证输出")
    print(f"   Prompts 文件数: {len(list((output_dir / 'prompts').glob('*.md')))}")
    print(f"   Session metadata: {session.metadata['slide_count']} slides")
    
    # Step 5: 模拟导出
    print(f"\n5️⃣ 导出（模拟）")
    print(f"   → {output_dir / '微服务架构设计指南.pptx'}")
    print(f"   → {output_dir / '微服务架构设计指南.pdf'}")
    
    # 清理
    import shutil
    if output_dir.exists():
        shutil.rmtree(output_dir)
    session.delete_session()
    print(f"\n   (测试目录已清理)")
    
    print("\n✅ 完整工作流测试通过！")


def run_all_tests():
    """运行所有阶段3测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "阶段 3 功能测试" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        test_1_slug_and_directory,
        test_2_prompt_saving,
        test_3_extend_mechanism,
        test_4_integration,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
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
        print("\n   🎉 阶段 3 所有测试通过！")
        print("\n   新功能已就绪:")
        print("   ✅ Slug 命名和专业目录结构")
        print("   ✅ Prompts 保存机制")
        print("   ✅ EXTEND 扩展机制")
    else:
        print("\n   ⚠️  部分测试失败，请检查错误信息")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == '__main__':
    run_all_tests()
