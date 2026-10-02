# 提示词收藏

旧成功案例位于 `modules/gpt-prompts/references/cases.md`，保留原文和来源；新收藏放在根目录 `collection/`，每条一个 JSON 文件。分类与入口一致：article、design、portrait、art、scene、edit。收藏是一个操作，不用它代替实际题材分类。

检索时先查 `collection/` 的 category/tags/title/prompt，再查旧案例。保存准确的完整提示词，不只保存摘要；原图存在时保存绝对路径或原始来源。不要把 API key、认证请求头或配置内容存进去。

用户说“收藏这个”“这个效果认可”是保存当前具体提示词的依据；用户仅要求试画不代表认可。状态：`draft` 待验证、`approved` 用户认可。标为 approved 时必须记录用户反馈原文。导入历史案例的旧描述保持历史属性，不擅自替它们增加当前验证结论。

```bash
python3 /Users/serva/.codex/skills/illustration-generator/scripts/collect_prompt.py \
  --title '极简产品广告' --category design --tag 产品 --tag 极简 \
  --prompt-file /absolute/prompt.txt --image /absolute/result.png \
  --status approved --feedback '这个效果认可，收藏一下' --model gpt-image-2
```

同样的提示词、分类、模型、图片和状态不会重复新增。原稿不覆盖；改写是新记录，`--source` 写原记录路径，便于追溯。用户要保存到外部笔记时按其要求另行处理；这个库保存的是 Skill 可直接复用的工作资料。
