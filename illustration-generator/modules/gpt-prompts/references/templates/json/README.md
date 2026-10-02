# JSON 模板变体系统

从 awesome-gpt-image-2 吸收的结构化 JSON 模板，适合 Agent 和自动化工作流调用。

## 设计原则

1. **JSON 是给 Agent 看的，不是给 GPT Image 2 的** — Agent 读取 JSON → 组装成自然语言 prompt → 传给生图 API
2. **常规模板 + JSON 模板并存** — 简单场景用常规模板快速出图，复杂/批量场景用 JSON 模板编程组装
3. **presets 是默认值** — 每个分类有合理的字段默认值，只需覆盖变化的部分

## 文件结构

```
json/
├── README.md              ← 你正在读的
├── ui_interface.json      ← UI界面设计
├── infographic.json       ← 图表与信息可视化
├── poster.json            ← 海报与排版
├── ecommerce.json         ← 商品与电商
├── brand_identity.json    ← 品牌与标志
├── architecture.json      ← 建筑与空间
├── photography.json       ← 摄影与写实
├── illustration.json      ← 插画与艺术
├── character.json         ← 人物与角色
├── narrative_scene.json   ← 场景与叙事
├── historical.json        ← 历史与古风题材
├── editorial.json         ← 文档与出版物
├── game_screenshot.json   ← 游戏截图
└── custom.json            ← 通用兜底模板
```

## JSON 模板统一格式

```json
{
  "category": "分类名",
  "description": "分类描述",
  "presets": { ... },
  "template": { ... },
  "pitfalls": [ ... ],
  "examples": [ ... ]
}
```

## 使用方式

```bash
# 列出所有 JSON 模板
python3 template_assembler.py list --json

# 查看某个分类的 JSON 模板
python3 template_assembler.py show --json -c ecommerce

# 从 JSON 模板组装 prompt
python3 template_assembler.py build-json -c ecommerce \
  --preset "电商主图" \
  --field product.name="无线降噪耳机" \
  --field product.material="磨砂黑+金属装饰" \
  --field product.angle="3/4侧视角"
```

## Agent 工作流

1. 用户描述需求 → Agent 识别分类和风格
2. 读取对应 JSON 模板文件
3. 用用户需求填充 template 字段（未指定的用 presets 默认值）
4. 将填充后的 JSON 转为自然语言 prompt
5. 传给 generate.py 生图
