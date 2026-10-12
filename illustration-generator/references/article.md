

# 文章配图分类

黄总已明确选择自己的生图系统。文章配图任务默认复用它，不要只提取风格后悄悄改用 Codex 内置生图；用户明确选择其他工具时遵从新选择。本文只负责文章配图；其他任务由统一入口选择分类。

## 唯一来源

- 阅读 `/Users/serva/.claude/skills/illustration-generator/SKILL.md`。
- 风格与布局：`/Users/serva/.claude/skills/shared-lib/illustration/`。
- 真实生图后端：`/Users/serva/.claude/skills/shared-lib/image_api.py` 中的 `ImageGenerator`。
- 配置与凭证继续留在原系统，不复制、不打印、不写入记忆。

## 执行

1. 对文章运行 `python3 /Users/serva/.claude/skills/illustration-generator/scripts/generate.py ARTICLE.md --preview`，展示实际推荐的三种风格及视觉差异。已选风格直接执行；用户要求“剩下几种”时，沿用上一轮选项，不替换成新推荐。
2. 从现有风格库读取规范，保持主题一致，给用户比较样式。现已扩充至 40 种精选风格（集成 Vibeshot 视觉图谱），实际可选项以脚本 `--list-styles` 为准。宝玉的封面规范与这个个人系统是两套来源，不混称。
3. 单张图调用本技能的 `scripts/generate_single.py`。批量文章配图按原 Skill 填写配置，使用文章副本，避免修改原稿。原脚本 `--preview` 只输出推荐，并不保证创建配置。
4. 保留用户要求的比例；未指定才以 16:9 作为文章配图默认值。旧 `--cover-only` 固定为 3:4，横版封面应走单图入口。传入比例不等于后端实际遵守；核对输出尺寸后才能声称是严格 16:9。
5. 检查标题、额外文字、色号、乱码、图标含义、裁切与水印。原风格可能要求无文字，不能再混入相反要求。不要把不合格图片命名为 final 或声称可用，不用大色块遮盖、裁掉主体来掩饰问题。
6. 记录实际使用的后端，保留原图和提示词，展示结果。后端失败最多完整尝试一轮配置的候选服务；仍失败就报告具体限制，不无限重试、不擅自切回内置生图。

单图调用（下列参数是命令用法，不是画面上的文字）：

```bash
python3 /Users/serva/.codex/skills/illustration-generator/scripts/generate_single.py \
  --content-file brief.txt --style editorial --layout infographic \
  --aspect 16:9 --output cover.png
```

`--dry-run` 仅检查提示词；`--list-styles` 列出原库的风格，不产生生图费用。不要将一次后端故障永久解释为凭证失效；例如 HTTP 401 只能证明该次请求未通过认证。
