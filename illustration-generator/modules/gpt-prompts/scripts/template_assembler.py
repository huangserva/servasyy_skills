#!/usr/bin/env python3
"""
Prompt Template Assembler — 支持 Markdown 模板 + JSON 模板

Markdown 模板：原有游戏截图模板系统（categories + elements）
JSON 模板：14分类结构化模板（presets + template + pitfalls + examples）

用法:
  # 列出所有模板（markdown + json）
  python3 template_assembler.py list
  python3 template_assembler.py list --json          # 只列 JSON 模板
  python3 template_assembler.py list --md             # 只列 Markdown 模板

  # 查看 JSON 模板详情
  python3 template_assembler.py show --json -c ecommerce
  python3 template_assembler.py show --json -c ecommerce --example 1

  # 查看 Markdown 模板（原有功能）
  python3 template_assembler.py show --category xianxia_mmo
  python3 template_assembler.py show --element health_bar

  # 从 JSON 模板组装 prompt
  python3 template_assembler.py build-json -c ecommerce \
    --field product.name="无线降噪耳机" \
    --field product.material="磨砂黑"

  # 从 Markdown 模板组装 prompt（原有功能）
  python3 template_assembler.py build --category xianxia_mmo --scene boss_fight \
    --var player_description="穿着粉色仙侠长裙的女角色"

  # 显示 JSON 模板的避坑指南
  python3 template_assembler.py pitfalls -c ecommerce
"""

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REFERENCES_DIR = os.path.join(SCRIPT_DIR, '..', 'references')
TEMPLATES_DIR = os.path.join(REFERENCES_DIR, 'templates')
MD_TEMPLATES_DIR = os.path.join(TEMPLATES_DIR, 'game_screenshot')
JSON_TEMPLATES_DIR = os.path.join(TEMPLATES_DIR, 'json')
CATEGORIES_DIR = os.path.join(MD_TEMPLATES_DIR, 'categories')
ELEMENTS_DIR = os.path.join(MD_TEMPLATES_DIR, 'elements')


# ──────────────────────────────────────
# JSON 模板加载器
# ──────────────────────────────────────

def load_json_template(category: str) -> dict:
    """加载 JSON 模板文件，支持精确/模糊/中文分类名匹配"""
    if not os.path.exists(JSON_TEMPLATES_DIR):
        return None

    # 精确匹配文件名
    candidates = [
        f"{category}.json",
        f"{category.replace('-', '_')}.json",
        f"{category.replace('_', '-')}.json",
    ]
    for c in candidates:
        path = os.path.join(JSON_TEMPLATES_DIR, c)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)

    # 遍历所有 JSON 文件，匹配 category 字段或文件名
    for fname in os.listdir(JSON_TEMPLATES_DIR):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(JSON_TEMPLATES_DIR, fname)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 匹配 JSON 内的 category 字段（支持中文）
        cat = data.get('category', '')
        if cat == category:
            return data

        # 模糊匹配：查询字符串是分类名或文件名的子串
        base = fname.replace('.json', '').replace('_', '').replace('-', '')
        query = category.replace('_', '').replace('-', '').replace(' ', '')
        if query and (query in base or base in query):
            return data

        # 中文部分匹配：查询字符串包含分类名的核心词
        if cat and any(word in category for word in cat.split('与') if len(word) > 1):
            return data
        if cat and any(word in cat for word in category.split('与') if len(word) > 1):
            return data

    return None


def list_json_templates():
    """列出所有 JSON 模板"""
    if not os.path.exists(JSON_TEMPLATES_DIR):
        return []

    results = []
    for fname in sorted(os.listdir(JSON_TEMPLATES_DIR)):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(JSON_TEMPLATES_DIR, fname)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        results.append({
            'file': fname,
            'category': data.get('category', fname.replace('.json', '')),
            'description': data.get('description', ''),
            'has_examples': len(data.get('examples', [])) > 0,
        })
    return results


def flatten_dict(d, parent_key='', sep='.'):
    """将嵌套 dict 展平为 key.path = value"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            items.append((new_key, v))
        else:
            items.append((new_key, v))
    return items


def deep_fill(template: dict, fields: dict, presets: dict = None) -> dict:
    """
    递归填充模板。
    fields: 用户提供的 dot-path 字段 (如 "product.name": "耳机")
    presets: 默认值（顶层 key 会尝试匹配 template 中任意深度的同名 key）
    """
    import copy
    result = copy.deepcopy(template)

    # 收集 template 中所有叶子节点路径
    template_leaves = {}  # {leaf_key_lowercase: [path_parts]}
    for path, _ in flatten_dict(template):
        parts = path.split('.')
        # 注册每一级 key（叶子 key 优先）
        leaf_key = parts[-1]
        if leaf_key not in template_leaves:
            template_leaves[leaf_key] = parts

    # 合并 presets：用同名匹配填入 template 对应位置
    if presets:
        for p_key, p_value in flatten_dict(presets):
            # presets 的 leaf key (如 "aspect_ratio")
            leaf = p_key.split('.')[-1]
            # 尝试匹配 template 中的同名叶子
            if leaf in template_leaves:
                # 找精确路径
                parts = template_leaves[leaf]
                _set_nested(result, parts, p_value)
            else:
                # 没有匹配路径，作为顶层约束附加
                result[p_key] = p_value

    # 覆盖用户字段（dot-path 精确匹配）
    for path, value in fields.items():
        _set_nested(result, path.split('.'), value)

    return result


def _set_nested(d, keys, value):
    """递归设置嵌套 dict 的值"""
    for key in keys[:-1]:
        if key not in d:
            d[key] = {}
        d = d[key]
    d[keys[-1]] = value


def json_to_prompt(filled: dict) -> str:
    """将填充后的 JSON 模板转为自然语言 prompt"""
    parts = []

    def _walk(obj, prefix=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                label = f"{prefix} {k}".strip() if prefix else k
                if isinstance(v, (dict, list)):
                    _walk(v, label)
                elif v and str(v).strip():
                    val = str(v)
                    if val.startswith('{{') and val.endswith('}}'):
                        return  # 未填充的跳过
                    parts.append(f"{label}: {val}")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    _walk(item, prefix)
                elif item and str(item).strip():
                    parts.append(f"{prefix}: {item}")

    _walk(filled)

    # 如果 prompt 太短（<3个字段），用 JSON dump 作为 fallback
    if len(parts) < 3:
        json_str = json.dumps(filled, ensure_ascii=False, indent=2)
        return json_str

    return ", ".join(parts)


# ──────────────────────────────────────
# Markdown 模板功能（原有，不变）
# ──────────────────────────────────────

def list_categories():
    """列出所有 Markdown 分类"""
    print("📦 游戏截图 Markdown 模板分类:\n")
    if not os.path.exists(CATEGORIES_DIR):
        print("  (无分类)")
        return

    for fname in sorted(os.listdir(CATEGORIES_DIR)):
        if fname.endswith('.md'):
            path = os.path.join(CATEGORIES_DIR, fname)
            name = fname.replace('.md', '')
            with open(path, 'r') as f:
                first_line = f.readline().strip()
                desc = first_line.lstrip('#').strip() if first_line.startswith('#') else first_line
            print(f"  • {name} — {desc}")

    print("\n🔧 UI元素组件:\n")
    if not os.path.exists(ELEMENTS_DIR):
        print("  (无元素)")
        return

    for fname in sorted(os.listdir(ELEMENTS_DIR)):
        if fname.endswith('.md'):
            print(f"  • {fname.replace('.md', '')}")


def show_category(name):
    """显示 Markdown 分类模板"""
    path = os.path.join(CATEGORIES_DIR, f"{name}.md")
    if not os.path.exists(path):
        for fname in os.listdir(CATEGORIES_DIR):
            if name.replace('_', '') in fname.replace('_', '').replace('-', ''):
                path = os.path.join(CATEGORIES_DIR, fname)
                name = fname.replace('.md', '')
                break

    if not os.path.exists(path):
        print(f"❌ 分类不存在: {name}")
        return

    with open(path, 'r') as f:
        print(f.read())


def show_element(name):
    """显示 UI 元素"""
    path = os.path.join(ELEMENTS_DIR, f"{name}.md")
    if not os.path.exists(path):
        print(f"❌ 元素不存在: {name}")
        return

    with open(path, 'r') as f:
        print(f.read())


def extract_variables(category_name):
    """提取 Markdown 模板变量"""
    path = os.path.join(CATEGORIES_DIR, f"{category_name}.md")
    if not os.path.exists(path):
        print(f"❌ 分类不存在: {category_name}")
        return

    with open(path, 'r') as f:
        content = f.read()

    variables = sorted(set(re.findall(r'\{\{(\w+)\}\}', content)))
    print(f"📋 {category_name} 模板变量:\n")
    for v in variables:
        print(f"  • {v}")
    print(f"\n共 {len(variables)} 个变量")


def build_prompt(args):
    """从 Markdown 模板拼装 prompt"""
    category = args.category
    scene = args.scene or 'boss_fight'
    variables = {}
    for v in (args.var or []):
        if '=' in v:
            k, val = v.split('=', 1)
            variables[k] = val

    path = os.path.join(CATEGORIES_DIR, f"{category}.md")
    if not os.path.exists(path):
        print(f"❌ 分类不存在: {category}")
        return

    with open(path, 'r') as f:
        content = f.read()

    scenes = re.split(r'###\s+', content)
    target_scene = None
    for section in scenes:
        if scene.replace('_', ' ').lower() in section.lower():
            code_blocks = re.findall(r'```\n(.*?)```', section, re.DOTALL)
            if code_blocks:
                target_scene = code_blocks[-1]
                break

    if not target_scene:
        code_blocks = re.findall(r'```\n(.*?)```', content, re.DOTALL)
        if code_blocks:
            target_scene = code_blocks[-1]
        else:
            print("❌ 未找到场景 prompt 模板")
            return

    for k, v in variables.items():
        target_scene = target_scene.replace(f'{{{{{k}}}}}', v)

    unfilled = re.findall(r'\{\{(\w+)\}\}', target_scene)
    if unfilled:
        print(f"⚠️  未填充变量: {', '.join(set(unfilled))}")

    print("=" * 60)
    print("生成的 Prompt:")
    print("=" * 60)
    print(target_scene)
    print("=" * 60)


# ──────────────────────────────────────
# JSON 模板子命令
# ──────────────────────────────────────

def cmd_list_json():
    """列出所有 JSON 模板"""
    templates = list_json_templates()
    if not templates:
        print("❌ 没有找到 JSON 模板")
        return

    print("📋 JSON 模板库（14 分类）:\n")
    for t in templates:
        ex_mark = "📄" if t['has_examples'] else "  "
        print(f"  {ex_mark} {t['category']:<16s} — {t['description']}")
    print(f"\n共 {len(templates)} 个模板")
    print("\n使用 show --json -c <分类名> 查看详情")
    print("使用 pitfalls -c <分类名> 查看避坑指南")


def cmd_show_json(category, example_idx=None):
    """显示 JSON 模板详情"""
    data = load_json_template(category)
    if not data:
        print(f"❌ JSON 模板不存在: {category}")
        print(f"   使用 list --json 查看所有可用模板")
        return

    if example_idx is not None:
        examples = data.get('examples', [])
        if example_idx < 1 or example_idx > len(examples):
            print(f"❌ 示例编号超出范围 (1-{len(examples)})")
            return
        ex = examples[example_idx - 1]
        print(f"📝 示例 {example_idx}: {ex.get('description', '')}\n")
        print(json.dumps(ex.get('filled', {}), ensure_ascii=False, indent=2))
        return

    print(f"📂 {data['category']}")
    print(f"   {data['description']}\n")

    print("🔧 Presets (默认值):")
    print(json.dumps(data.get('presets', {}), ensure_ascii=False, indent=2))

    print("\n📐 Template (骨架):")
    print(json.dumps(data.get('template', {}), ensure_ascii=False, indent=2))

    pitfalls = data.get('pitfalls', [])
    if pitfalls:
        print(f"\n⚠️  避坑指南 ({len(pitfalls)} 条):")
        for i, p in enumerate(pitfalls, 1):
            print(f"  {i}. {p}")

    examples = data.get('examples', [])
    if examples:
        print(f"\n📄 示例 ({len(examples)} 个): 使用 --example N 查看")


def cmd_build_json(args):
    """从 JSON 模板组装 prompt"""
    data = load_json_template(args.category)
    if not data:
        print(f"❌ JSON 模板不存在: {args.category}")
        return

    # 解析用户字段
    fields = {}
    for f in (args.field or []):
        if '=' in f:
            k, v = f.split('=', 1)
            # 尝试解析 JSON 值（数组等）
            try:
                fields[k] = json.loads(v)
            except (json.JSONDecodeError, ValueError):
                fields[k] = v

    # 填充模板
    filled = deep_fill(
        data.get('template', {}),
        fields,
        presets=data.get('presets', {})
    )

    # 转为 prompt
    prompt = json_to_prompt(filled)

    # 检查未填充的占位符
    unfilled = re.findall(r'\{\{(\w+)\}\}', prompt)
    if unfilled:
        print(f"⚠️  未填充字段: {', '.join(set(unfilled))}")
        print(f"   使用 --field key.path=value 来填充\n")

    print("=" * 60)
    print("生成的 Prompt:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)

    # 也输出填充后的 JSON（供调试）
    if args.verbose:
        print("\n📊 填充后的 JSON 结构:")
        print(json.dumps(filled, ensure_ascii=False, indent=2))

    print(f"\n📝 可直接传给 generate.py:")
    print(f"   python3 ~/.hermes/skills/creative/image-generator/scripts/generate.py \\")
    print(f'     "{prompt[:80]}..." \\')
    print(f"     --model gpt-image-2 --ratio 9:16")


def cmd_pitfalls(category):
    """显示避坑指南"""
    data = load_json_template(category)
    if not data:
        print(f"❌ JSON 模板不存在: {category}")
        return

    pitfalls = data.get('pitfalls', [])
    if not pitfalls:
        print(f"ℹ️  {category} 没有避坑指南")
        return

    print(f"⚠️  {data['category']} — 避坑指南 ({len(pitfalls)} 条):\n")
    for i, p in enumerate(pitfalls, 1):
        print(f"  {i}. {p}")


def cmd_vars_json(category):
    """列出 JSON 模板的所有可填充字段"""
    data = load_json_template(category)
    if not data:
        print(f"❌ JSON 模板不存在: {category}")
        return

    template = data.get('template', {})
    presets = data.get('presets', {})

    print(f"📋 {data['category']} — 可填充字段:\n")

    # 展平模板，列出所有叶子节点
    flat_template = flatten_dict(template)
    flat_presets = dict(flatten_dict(presets)) if presets else {}

    filled_by_preset = set()
    unfilled = []

    for path, value in flat_template:
        if path in flat_presets:
            filled_by_preset.add(path)
        elif isinstance(value, str) and value.startswith('{{'):
            unfilled.append(path)
        else:
            unfilled.append(path)

    if filled_by_preset:
        print("✅ 有默认值（presets 已覆盖）:")
        for p in sorted(filled_by_preset):
            print(f"   {p}")
    if unfilled:
        print("\n🔲 需要填充:")
        for p in sorted(unfilled):
            print(f"   {p}")

    print(f"\n共 {len(flat_template)} 个字段")


# ──────────────────────────────────────
# 主入口
# ──────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Prompt 模板拼装器 (Markdown + JSON)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  list                   列出所有模板
  list --json            只列 JSON 模板
  show --json -c 海报    查看 JSON 模板详情
  build-json -c 海报 --field ...   从 JSON 模板组装 prompt
  pitfalls -c 海报       查看避坑指南
"""
    )
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # ── list ──
    list_p = subparsers.add_parser('list', help='列出所有模板')
    list_p.add_argument('--json', action='store_true', help='只列出 JSON 模板')
    list_p.add_argument('--md', action='store_true', help='只列出 Markdown 模板')

    # ── show ──
    show_p = subparsers.add_parser('show', help='查看模板详情')
    show_p.add_argument('--json', action='store_true', help='查看 JSON 模板')
    show_p.add_argument('--category', '-c', help='分类名')
    show_p.add_argument('--element', '-e', help='元素名 (Markdown)')
    show_p.add_argument('--example', type=int, help='查看第 N 个示例')

    # ── vars ──
    vars_p = subparsers.add_parser('vars', help='列出模板变量/字段')
    vars_p.add_argument('--category', '-c', help='分类名')
    vars_p.add_argument('--json', action='store_true', help='JSON 模板字段')

    # ── build (Markdown) ──
    build_p = subparsers.add_parser('build', help='从 Markdown 模板拼装 prompt')
    build_p.add_argument('--category', '-c', required=True, help='分类名')
    build_p.add_argument('--scene', '-s', help='场景类型')
    build_p.add_argument('--var', '-v', action='append', help='变量 KEY=VALUE')

    # ── build-json ──
    build_json_p = subparsers.add_parser('build-json', help='从 JSON 模板拼装 prompt')
    build_json_p.add_argument('--category', '-c', required=True, help='分类名')
    build_json_p.add_argument('--field', '-f', action='append', help='字段 path=value')
    build_json_p.add_argument('--verbose', '-V', action='store_true', help='显示填充后 JSON')

    # ── pitfalls ──
    pitfalls_p = subparsers.add_parser('pitfalls', help='显示 JSON 模板避坑指南')
    pitfalls_p.add_argument('--category', '-c', required=True, help='分类名')

    args = parser.parse_args()

    if args.command == 'list':
        if args.json:
            cmd_list_json()
        elif args.md:
            list_categories()
        else:
            # 默认都列出
            print("=" * 60)
            cmd_list_json()
            print("\n" + "=" * 60)
            list_categories()

    elif args.command == 'show':
        if args.json and args.category:
            cmd_show_json(args.category, args.example)
        elif args.category:
            show_category(args.category)
        elif args.element:
            show_element(args.element)
        else:
            print("请指定 --category (-c) 和/或 --json")

    elif args.command == 'vars':
        if args.json and args.category:
            cmd_vars_json(args.category)
        elif args.category:
            extract_variables(args.category)
        else:
            print("请指定 --category (-c)")

    elif args.command == 'build':
        build_prompt(args)

    elif args.command == 'build-json':
        cmd_build_json(args)

    elif args.command == 'pitfalls':
        cmd_pitfalls(args.category)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
