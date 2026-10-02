# 生图后端与执行

统一的是用户入口和资料分类；实际保留现有可用后端。凭证继续留在 Claude/Hermes 的配置，不复制、不打印、不写进收藏。

## 文章配图

沿用 [文章配图](article.md) 的 `scripts/generate_single.py` 与 Claude 共享库。它会套用文章风格规范，适合文章配图，不要把其他类别的完整提示词再套一次文章画风。

## 通用图片和 GPT 提示词

黄总已指定静态生图默认走本地 4090 的 Qwen-Image 2.1：[qwen-image-21-t2i 模块](../modules/qwen-image-21-t2i/GUIDE.md)。

```bash
python3 /Users/serva/.codex/skills/illustration-generator/modules/qwen-image-21-t2i/scripts/run_qwen21_t2i.py \
  --prompt-file /absolute/brief.txt --output /absolute/cover.png --aspect 16:9
```

原 GPT 图像后端保留（`scripts/generate_gpt.py`，模型标识 `gpt-image-2`），黄总明确指定时使用：

```bash
python3 /Users/serva/.codex/skills/illustration-generator/scripts/generate_gpt.py \
  --prompt-file /absolute/brief.txt --aspect 16:9 --output /absolute/cover.png
```

`--dry-run` 输出提示词和请求参数，不发送请求。实际模型配置以原后端为准；请求失败时报告失败，不静默换模型。一次运行失败后只针对明确原因修正，最多再尝试一次，仍失败则保留提示词并说明限制。多图用不同输出路径，不覆盖已有产物。

## 编辑与多图连续性

优先服从当前宿主要求：当前工具要求使用内置 `image_gen` 进行编辑时，通过该工具传入参考图并说明实际后端；用户明确要求其他工具且宿主允许时才按原后端的 `--image` 接口执行。不要通过新建图的名义绕过编辑要求。

多阶段连续角色/分镜生成按对应模块检查模型、工作流、参考图与运行队列；不因为有一个模板就自动启动整条视频流程。

## 验收与限制

本地文件式入口检查后端文件存在、输入非空、输出不覆盖；生成后打开图像验证尺寸。实际出图服务未运行时只能声称路径/离线检查通过。展示原图，用绝对路径链接文件；保存完整提示词与实际后端信息。用户要透明背景时使用支持透明输出的工具并检查 alpha 通道，不能只生成棋盘背景。
