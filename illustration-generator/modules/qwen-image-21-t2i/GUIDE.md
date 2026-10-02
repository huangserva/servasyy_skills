# Qwen-Image 2.1 本地文生图（4090）

统一生图入口的本地文生图后端模块。模型：`qwen_image_2.1_bf16`（20B 级全精度，不再走中转 API 的 gpt-image 路线——黄总已明确要求静态生图用 4090 上的 qwen-image2.1）。

## 后端拓扑

- 机器：`newgpu`（SSH 配置，经 ali-jump 跳转），RTX 4090 48G
- 实例：`/home/admin01/ComfyUI-qi21`（ComfyUI 开发版 fork，含原生 `TextEncodeQwenImage21` / `QwenImage21Cache` 节点）
- 端口：**8192**（本模块专用，127.0.0.1 只监听，经 SSH 访问）
- 模型文件（`models/` 下，均为符号链接到 `/home/admin01/models/Comfy-Org--Qwen-Image-2.1/`）：
  - UNET：`qwen_image_2.1_bf16.safetensors`（14G，另有 `int8_convrot` 6.8G 备用）
  - CLIP：`qwen3vl_8b_bf16.safetensors`（type=`qwen_image`）
  - VAE：`qwen_image_2.1_vae_bf16.safetensors`

### 端口纪律（重要）

- **8188 是机器守护进程管理的旧版 ComfyUI**（`imports/rented_.../ComfyUI`，`venv_old_broken`），没有 Qwen-Image 2.1 节点，其 VAE 解析器也不认识 2.1 VAE（标准 KSampler 路线会报 WanVAE shape mismatch）。**不要杀它、不要抢 8188**——杀掉后守护会自动拉回旧版。
- 本模块固定用 8192。启动命令（`setsid` 脱离会话，防止 SSH 断开连带杀进程）：

```bash
ssh newgpu "cd /home/admin01/ComfyUI-qi21 && setsid bash -c \
'/home/admin01/imports/rented_175_155_64_171/ComfyUI-H3/.venv/bin/python main.py \
--listen 127.0.0.1 --port 8192 > /tmp/comfyui-qi21-8192.log 2>&1 < /dev/null &' && echo LAUNCHED"
```

- qi21 目录没有自己的 venv，借用 ComfyUI-H3 的 venv（torch 2.13+cu130，已验证可 import 该 fork 的 comfy 模块）。
- 显存：bf16 UNET 14G + CLIP 17G + VAE 0.6G，约 32G 常驻。若 4090 显存被其他任务占满（<35G 空闲），先与黄总确认后再清腾，不要擅自停其他进程。历史教训：2026-09-30 停过两个 ComfyUI-H3 进程腾显存，属一次性授权。

## 参数

| 参数 | 值 |
|---|---|
| sampler / scheduler | `er_sde` / `simple` |
| steps / cfg | 20 / 1.0 |
| denoise | 1.0 |
| 尺寸档位 | 1:1 1344² · 3:4 1152×1536 · 16:9 1536×864 · 9:16 864×1536 · 4:3 1536×1152 |
| 单张耗时 | 模型常驻时约 30-90 秒；冷启动（加载模型）+2-3 分钟 |
| 提交协议 | ComfyUI 新版：body 必须包一层 `{"prompt": {...}}`，裸工作流 JSON 会报 `no_prompt` |

## 用法

```bash
python3 MODULE/scripts/run_qwen21_t2i.py --prompt-file brief.txt \
  --output out.png --aspect 16:9
```

- 环境变量：`QI21_PORT`（默认 8192）、`QI21_SSH`（默认 `ssh -o ConnectTimeout=10 newgpu`）、`QI21_OUTPUT_DIR`（默认 `/home/admin01/ComfyUI-qi21/output`）。
- 产物旁自动写 `<out>.prompt.txt` 与 `<out>.request.json`（含 seed、steps、prompt_id），验收与留档规则同 [backends.md](../../references/backends.md)。
- 失败重试：SSH 瞬断（banner exchange timeout）属网络抖动，重跑即可；生图本身失败按后端规则最多修正一次。

## 批量

63 风格样例（2026-09-30）全量跑通记录见 [../../references/cases.md](../../references/cases.md) 的 qwen-image 2.1 段落；批量脚本模式：manifest（prompt/aspect/output 三列）+ 顺序循环 + 断点续跑（输出已存在则 SKIP）。

## 已知坑

1. **stdin 泄漏**：批处理循环里 runner 的子进程（ssh）会继承循环的 stdin 流，把剩余 manifest 行经 SSH 转发吃掉——runner 启动时 `os.dup2(devnull, 0)` 且所有 ssh 调用 `stdin=DEVNULL`。
2. **nohup 不可靠**：`nohup` 起的进程在 SSH 会话被强杀时仍可能死掉，必须 `setsid` + 三向重定向。
3. **旧版 ComfyUI 抢端口**：见"端口纪律"。
4. 文字渲染：中文大体可用，长英文标题仍可能乱码（如 ACG 海报案例）；要精确文字时写死内容并在验收时逐字核对。
