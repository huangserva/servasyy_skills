---
name: twitter-crawler
description: Twitter 推文爬取器 - 指定用户名爬取推文，保存为 Markdown 格式，支持自定义数量和字段
allowed-tools: Bash, Read, Write, Edit
---

# Twitter 推文爬取器

## 概述

爬取指定 Twitter 用户的推文，保存为 Markdown 格式。

## 使用方法

### 基础用法

```bash
cd ~/.claude/skills/twitter-crawler
python3 scripts/fetch_tweets.py <用户名>
```

### 完整参数

```bash
python3 scripts/fetch_tweets.py <用户名> [选项]

选项：
  -n, --limit N        获取推文数量（默认10）
  -p, --pages N        获取页数（默认1，每页约20条）
  -o, --output PATH    输出文件路径（默认 outputs/{用户名}.md）
  --json               同时输出 JSON 格式
  --interval SECONDS   请求间隔秒数（默认5，防止频率限制）
  --no-user-info       不获取用户信息
  --title TITLE        自定义 Markdown 标题
  --fields FIELDS      包含的字段，逗号分隔
  --auth-token TOKEN   指定 auth_token
```

### 频率限制

Twitter API 有频率限制，脚本内置了以下保护机制：
- 默认每次请求间隔 5 秒
- 自动添加随机抖动（0.5-2秒）避免被检测
- 可通过 `--interval` 调整间隔时间
- 获取超过 20 条推文时自动分页

### 字段选项

`--fields` 可选值（逗号分隔）：
- `text` - 推文内容
- `time` - 发布时间
- `likes` - 点赞数
- `retweets` - 转发数
- `replies` - 回复数
- `views` - 浏览量
- `url` - 推文链接
- `media` - 媒体（图片）

## 示例

### 示例1：基础爬取

```bash
python3 scripts/fetch_tweets.py VoxcatAI
```

输出：`outputs/VoxcatAI.md`

### 示例2：指定数量和输出路径

```bash
python3 scripts/fetch_tweets.py elonmusk -n 20 -o ~/Desktop/elon.md
```

### 示例3：只要内容和链接

```bash
python3 scripts/fetch_tweets.py sama --fields text,url
```

### 示例4：同时输出 JSON

```bash
python3 scripts/fetch_tweets.py OpenAI -n 15 --json
```

输出：
- `outputs/OpenAI.md`
- `outputs/OpenAI.json`

### 示例5：自定义标题

```bash
python3 scripts/fetch_tweets.py VoxcatAI --title "VoxCat 的 Prompt 分享"
```

## 输出格式

### Markdown 格式

```markdown
# @用户名 的推文

> 爬取时间: 2026-01-11 12:00:00
> 推文数量: 10

## 用户信息

- **名称**: xxx
- **用户名**: @xxx
- **粉丝**: 1,000
- **简介**: xxx

## 推文列表

### 1. 推文

**时间**: 2026-01-11 10:00:00

> 推文内容...

**互动**: ❤️ 100 | 🔁 20 | 💬 5

**链接**: [https://twitter.com/xxx/status/xxx](...)

---
```

### JSON 格式

```json
{
  "user": {
    "name": "xxx",
    "username": "xxx",
    "followers": 1000,
    ...
  },
  "tweets": [
    {
      "id": "xxx",
      "text": "xxx",
      "created_at": "2026-01-11 10:00:00",
      "likes": 100,
      "retweets": 20,
      ...
    }
  ],
  "fetched_at": "2026-01-11T12:00:00"
}
```

## 配置

### auth_token

脚本会自动从 `~/Documents/trend-crawler-master/trend-crawler/config.yaml` 读取 `auth_token`。

如果需要单独配置，创建 `~/.claude/skills/twitter-crawler/config.yaml`：

```yaml
twitter_accounts:
  auth_token: "你的auth_token"
```

### 获取 auth_token

1. 登录 Twitter 网页版
2. 打开开发者工具 (F12) → Application → Cookies
3. 找到 `auth_token` 的值

## 依赖

- tweety-ns（从 trend-crawler 项目的 venv 加载）
- pyyaml

## 注意事项

1. **频率限制**：Twitter 有 API 频率限制，建议间隔使用
2. **auth_token 过期**：如果遇到错误，可能需要更新 auth_token
3. **访客模式**：不配置 auth_token 也能使用，但可能受限
