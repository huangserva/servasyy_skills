#!/usr/bin/env python3
"""列出所有可用风格，供快速查阅。"""

import sys, os, json

# 直接读 styles.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path
# 从 references 目录导入
ref_dir = Path(__file__).resolve().parent.parent / "references"
sys.path.insert(0, str(ref_dir))
from styles import STYLES

def list_all():
    result = {}
    for cat_id, cat in STYLES.items():
        result[cat_id] = {
            "description": cat["description"],
            "styles": list(cat["styles"].keys())
        }
    return result

def show_style(name):
    """显示某个风格的详情"""
    for cat_id, cat in STYLES.items():
        if name in cat["styles"]:
            s = cat["styles"][name]
            return {
                "category": cat_id,
                "name": name,
                "instruction": s.get("style_instruction", s.get("instruction", "")),
                "best_for": s["best_for"],
                "tips": s["tips"],
                "example": s["example"],
            }
    return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="风格库查询")
    parser.add_argument("action", nargs="?", default="list", choices=["list", "show"], help="list=列出所有, show=查看详情")
    parser.add_argument("--name", "-n", help="风格名称（show时必填）")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    args = parser.parse_args()

    if args.action == "list":
        data = list_all()
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            for cat_id, cat in data.items():
                print(f"\n📦 {cat_id} — {cat['description']}")
                for s in cat["styles"]:
                    print(f"   • {s}")

    elif args.action == "show":
        if not args.name:
            print("请用 --name 指定风格名称，如: --name '仙侠MMO游戏截图'")
            sys.exit(1)
        result = show_style(args.name)
        if not result:
            # 模糊搜索
            matches = []
            for cat_id, cat in STYLES.items():
                for name in cat["styles"]:
                    if args.name.lower() in name.lower():
                        matches.append(name)
            if matches:
                print(f"没找到精确匹配，你是不是想找: {', '.join(matches)}")
            else:
                print(f"未找到风格: {args.name}")
            sys.exit(1)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n🎨 {result['name']}")
            print(f"   类别: {result['category']}")
            print(f"   风格指令: {result['instruction']}")
            print(f"   适用: {result['best_for']}")
            print(f"   技巧: {result['tips']}")
            print(f"   示例: {result['example']}")
