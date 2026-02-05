---
name: md-to-pdf
description: Convert markdown documents to PDF with optional illustrations. Can automatically call illustration-generator if images are missing. Supports Chinese fonts and custom styling.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite
---

# Markdown to PDF Converter

将 Markdown 文档转换为 PDF，支持自动配图。

## 功能

- 📄 Markdown → PDF 转换
- 🎨 可选：自动调用 illustration-generator 生成配图
- 🇨🇳 中文字体支持
- 🎯 纽约客风格排版

## 使用方法

### 基础用法

```bash
# 仅转换（需要图片已存在）
/md-to-pdf <markdown_file>

# 自动生成配图后转换
/md-to-pdf <markdown_file> --with-illustrations

# 指定输出路径
/md-to-pdf <markdown_file> -o output.pdf
```

### 工作流程

1. 检查图片是否存在
2. 如果 `--with-illustrations`：调用 illustration-generator
3. 使用 WeasyPrint 转换 MD → PDF
4. 输出 PDF 文件

## 输出

- PDF 文件：与 MD 同名，`.pdf` 后缀
- 包含封面、配图、格式化文本

## 依赖

- WeasyPrint
- illustration-generator (可选)
