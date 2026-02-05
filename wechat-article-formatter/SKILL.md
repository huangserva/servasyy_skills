---
name: wechat-article-formatter
description: 将 Markdown 文章转换为微信公众号 HTML 格式，支持自动插入配图、微信样式优化。
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# WeChat Article Formatter（微信文章格式化）

将 Markdown 文章转换为可直接粘贴到微信公众号编辑器的 HTML 格式。

## 核心能力

- 📝 Markdown → 微信 HTML
- 🎨 自动插入配图（从 illustrations 目录）
- 🎯 微信样式优化（字体、间距、引用块）
- 📱 移动端适配

## 使用方式

```bash
# 基础用法
/wechat-article-formatter article.md

# 指定配图目录
/wechat-article-formatter article.md --images ./illustrations/
```

---

## 工作流程（5步）

### Step 1: 读取 Markdown 文章

读取输入的 Markdown 文件内容。

### Step 2: 查找配图

检查同目录下是否有 `illustrations/` 目录：
- 如有，读取所有图片文件
- 按章节匹配图片（根据文件名前缀 01-, 02- 等）

### Step 3: 转换为 HTML

**转换规则：**

| Markdown | 微信 HTML |
|----------|-----------|
| `# 标题` | `<h1 style="...">标题</h1>` |
| `## 小标题` | `<h2 style="...">小标题</h2>` |
| `**加粗**` | `<strong style="color:#d4237a;">加粗</strong>` |
| `> 引用` | `<blockquote style="...">引用</blockquote>` |
| 段落 | `<p style="...">段落</p>` |
| 表格 | `<table style="...">...</table>` |

**微信样式规范：**
```css
/* 正文 */
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
font-size: 16px;
line-height: 1.8;
color: #333;

/* 标题 */
h1: font-size: 22px; font-weight: bold; margin: 20px 0;
h2: font-size: 18px; font-weight: bold; margin: 15px 0; border-left: 4px solid #d4237a; padding-left: 10px;

/* 引用块 */
blockquote: background: #f7f7f7; border-left: 4px solid #d4237a; padding: 15px; margin: 15px 0;

/* 加粗 */
strong: color: #d4237a;

/* 段落 */
p: margin: 15px 0; text-align: justify;
```

### Step 4: 插入配图

在每个 H2 章节后插入对应的配图：

```html
<figure style="margin: 20px 0; text-align: center;">
  <img src="data:image/png;base64,{base64_data}" style="max-width: 100%; border-radius: 8px;" />
</figure>
```

**图片处理：**
- 将图片转换为 base64 内嵌（便于直接粘贴）
- 或输出图片 URL 列表（需要手动上传）

### Step 5: 输出 HTML

保存为 `{filename}_wechat.html`，可直接复制粘贴到微信公众号编辑器。

---

## 输出示例

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>文章标题</title>
</head>
<body style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">

<h1 style="font-size: 22px; font-weight: bold; text-align: center; margin-bottom: 30px;">
  50万秦军去哪了？基因和语言揭开了一个惊天秘密
</h1>

<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0;">
  你有没有想过这样一个问题：
</p>

<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0;">
  <strong style="color: #d4237a;">秦始皇派去岭南的50万大军，后来都去哪了？</strong>
</p>

<!-- 更多内容... -->

</body>
</html>
```

---

## 与其他 Skill 配合

| 顺序 | Skill | 功能 |
|------|-------|------|
| 1 | document-writer | 生成 Markdown 文章 |
| 2 | illustration-generator | 为文章生成配图 |
| 3 | **wechat-article-formatter** | 格式化为微信 HTML |
| 4 | wechat-publisher | 发布到微信公众号 |
