#!/usr/bin/env python3
"""验证 Markdown Illustrator Skill 是否正确安装"""

import sys
import json
from pathlib import Path

SKILL_DIR = Path.home() / '.claude' / 'skills' / 'markdown-illustrator'

def check_file(filename, required=True):
    """检查文件是否存在"""
    filepath = SKILL_DIR / filename
    exists = filepath.exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    print(f"   {status} {filename}")
    return exists

def check_skill_structure():
    """检查Skill文件结构"""
    print("\n📋 检查Skill文件结构...")
    
    required_files = {
        'skill.md': True,
        'skill.json': True,
        'skill.prompt': True,
        'illustrate.py': True,
        'README.md': False,
        'config.yaml': False,
        'INSTALL.md': False,
    }
    
    all_required_exist = True
    for filename, required in required_files.items():
        exists = check_file(filename, required)
        if required and not exists:
            all_required_exist = False
    
    return all_required_exist

def validate_skill_json():
    """验证skill.json格式"""
    print("\n📦 验证skill.json...")
    
    skill_json_path = SKILL_DIR / 'skill.json'
    
    try:
        with open(skill_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_fields = ['name', 'version', 'description', 'entry']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            print(f"   ❌ 缺少必要字段: {', '.join(missing_fields)}")
            return False
        
        print(f"   ✅ name: {data['name']}")
        print(f"   ✅ version: {data['version']}")
        print(f"   ✅ entry: {data['entry']}")
        print(f"   ✅ providers: {len(data.get('providers', {}))} 个")
        print(f"   ✅ styles: {len(data.get('styles', {}))} 种")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 读取失败: {e}")
        return False

def check_dependencies():
    """检查依赖"""
    print("\n🔗 检查依赖...")
    
    # 检查shared-lib
    shared_lib = Path.home() / '.claude' / 'skills' / 'shared-lib' / 'image_api.py'
    if shared_lib.exists():
        print(f"   ✅ shared-lib/image_api.py")
    else:
        print(f"   ❌ shared-lib/image_api.py (缺失)")
        return False
    
    # 检查Python模块
    try:
        import requests
        print(f"   ✅ requests")
    except ImportError:
        print(f"   ⚠️  requests (未安装，需要: pip install requests)")
    
    try:
        import PIL
        print(f"   ✅ pillow")
    except ImportError:
        print(f"   ⚠️  pillow (未安装，需要: pip install pillow)")
    
    return True

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║     🔍 Markdown Illustrator Skill - 安装验证               ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    if not SKILL_DIR.exists():
        print(f"\n❌ Skill目录不存在: {SKILL_DIR}")
        sys.exit(1)
    
    print(f"\n📁 Skill位置: {SKILL_DIR}")
    
    # 检查文件结构
    structure_ok = check_skill_structure()
    
    # 验证skill.json
    json_ok = validate_skill_json()
    
    # 检查依赖
    deps_ok = check_dependencies()
    
    # 总结
    print("\n" + "="*60)
    
    if structure_ok and json_ok and deps_ok:
        print("✅ Skill验证通过！")
        print("\n🎯 激活方式:")
        print('   在Claude对话中说: "用markdown-illustrator给我的文档配图"')
        print("\n💻 命令行测试:")
        print(f"   cd {SKILL_DIR}")
        print("   python3 illustrate.py <markdown_file> [options]")
        print("="*60)
        sys.exit(0)
    else:
        print("❌ Skill验证失败，请检查上述错误")
        print("="*60)
        sys.exit(1)

if __name__ == '__main__':
    main()
