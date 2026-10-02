# 通用提示词、风格库与模板

从 Hermes 的 `prompt-generator-gpt` 迁入的 Codex 资料。此目录是统一生图入口的内部模块，不单独注册 Skill。

## 按需查找

命令中的 `MODULE` 代表本文件所在目录。先定位该绝对路径，再运行脚本。

- `python3 MODULE/scripts/list_styles.py list`：列出真实分类与风格。
- `python3 MODULE/scripts/list_styles.py show --name '风格名'`：查看对应视觉规则和示例。
- `python3 MODULE/scripts/template_assembler.py list --json`：列出结构化模板。
- `python3 MODULE/scripts/template_assembler.py show --json -c poster`：查看海报模板。
- `python3 MODULE/scripts/template_assembler.py build-json -c ecommerce --field product.name='无线降噪耳机'`：填充产品模板。
- 游戏截图：`template_assembler.py list --md`，再按游戏类别、场景与界面组件拼装。

`references/styles.py` 是完整风格库；`references/templates/json/` 按交付类型分类；`references/templates/game_screenshot/` 是复杂游戏画面的拼装模板。数量以文件和查询结果为准。

## 组织提示词

按用途、主体、场景、构图、精确文字、媒介风格、保留项、限制和验收目标组织，只使用与当前任务有关的字段。避免只堆形容词；保持用户指定内容和留白。组装器返回模板/默认值时继续用用户需求补全，不直接把未替换变量交给生图后端。

编辑先写清保留什么、只改什么；多参考图逐张指定职责。参考图的视觉媒介是观察或推断，不凭画风断言其真实制作来源。

## 收藏复用

[历史案例](references/cases.md) 保留旧系统的提示词、反馈和经验，先按主题检索再读相关段落。历史成绩、价格、耗时与第三方模型说明不保证当前有效。新收藏统一写入根目录 `collection/`，见 [收藏规则](../../references/collection.md)。不要一份写 Hermes、一份写 Codex，造成两个版本难以追踪；本次迁入是独立快照，不会自动同步 Hermes 后续改动。

## 生成与交付

完成提示词后使用统一入口的 [后端规则](../../references/backends.md)。不要使用原 Hermes 的聊天/飞书工具名。用户已要求出图时直接执行；无新增重要歧义就不重复确认。
