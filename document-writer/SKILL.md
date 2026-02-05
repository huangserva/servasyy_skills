---
name: document-writer
description: 多风格文档写作技能。支持乔木、小红书、Dankoe、微信公众号、Twitter等5种写作风格。Claude 根据内容智能选择风格，按规范撰写文章。
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite
---

# Document Writer（多风格文档写作）

将任意主题或素材转化为指定风格的文章。

## 核心能力

- 🎨 **5种写作风格**：qiaomu、xiaohongshu、dankoe、wechat、twitter
- 🧠 **Claude 智能决策**：阅读内容后判断类型，选择合适风格
- 📝 **纯Markdown输出**：专注写作，配图交给 `illustration-generator`
- ⚡ **风格转换**：长文→短文→推特，一键转换

## 使用方式

```bash
# 指定风格写作
/document-writer "秦军消失之谜" --style wechat

# 从素材改写
/document-writer source.md --style qiaomu

# 风格转换
/document-writer convert article.md --to xiaohongshu
```

## 可用风格

| 风格 | 字数 | 特点 | 适用场景 |
|------|------|------|----------|
| `qiaomu` | 8000-10000 | 口语化、对话感、生活化类比 | 技术论文解读、深度科普 |
| `xiaohongshu` | 800-1200 | 情绪化、去爹味、emoji点缀 | 种草文、干货分享 |
| `dankoe` | 5000-8000 | 挑衅开场、反常识、长短句交替 | 深度思考、观点输出 |
| `wechat` | 3000-6000 | 短段落、重点加粗、结尾互动 | 公众号文章、行业分析 |
| `twitter` | 100-280 | 钩子开头、精炼有力 | Twitter帖子、知识卡片 |

---

## 工作流程（7步）

### Step 1: 读取输入

**Claude 执行：**
1. 识别用户输入类型：
   - 主题文字 → 直接使用
   - 文件路径 → 读取文件内容
2. 记录输入内容

### Step 2: 选择风格

**如果用户指定了 `--style`：**
- 直接使用指定风格

**如果用户未指定风格：**
- Claude 阅读内容，判断内容类型（历史/技术/生活/商业...）
- Claude 选择最合适的风格
- 告知用户选择结果和理由

**调用 shared-lib 获取可用风格：**
```python
import sys
sys.path.insert(0, str(Path.home() / '.claude' / 'skills' / 'shared-lib'))
from writing import list_styles

print(list_styles())  # ['qiaomu', 'xiaohongshu', 'dankoe', 'wechat', 'twitter']
```

### Step 3: 获取风格规范

**调用 shared-lib 获取风格提示词：**
```python
from writing import get_style_prompt, get_style_info

# 获取风格详情
info = get_style_info('wechat')
print(f"风格: {info['display_name']}")
print(f"字数: {info['word_count']['min']}-{info['word_count']['max']}")

# 获取完整风格指南（给 Claude 用）
prompt = get_style_prompt('wechat')
print(prompt)
```

### Step 4: 撰写文章

**Claude 按风格规范撰写：**

1. 阅读风格指南中的：
   - 核心特征
   - 结构要求
   - 禁止使用项
   - 字数要求

2. 按规范撰写文章：
   - 遵循结构要求（opening → body → closing）
   - 控制字数在范围内
   - 避免禁止项

3. 输出完整 Markdown 文章

### Step 5: 质量自检

**Claude 根据风格执行自检：**

**qiaomu 风格检查：**
- [ ] 术语解释 ≥ 15处
- [ ] 生活化类比 ≥ 3处
- [ ] 数据表格 ≥ 1个
- [ ] 破折号 = 0个
- [ ] 中文标点 100%

**wechat 风格检查：**
- [ ] 字数 3000-6000
- [ ] 每段 ≤ 5行
- [ ] 有小标题分隔
- [ ] 重点加粗
- [ ] 结尾有互动引导

**xiaohongshu 风格检查：**
- [ ] 字数 800-1200
- [ ] 每段 ≤ 3行
- [ ] 有情绪转折
- [ ] 无爹味表达
- [ ] 有互动钩子

**发现问题 → 静默修复 → 继续**

### Step 6: 保存输出

**创建输出目录和文件：**

```
{output_dir}/
├── {title}.md           # Markdown文章
└── metadata.json        # 元数据
```

**metadata.json 格式：**
```json
{
  "title": "文章标题",
  "style": "wechat",
  "word_count": 3500,
  "source": "source.md 或 null",
  "created_at": "2026-01-26T10:00:00",
  "generator": "document-writer"
}
```

### Step 7: 输出总结

```
✅ 文章生成完成！

📄 文件: {title}.md
📝 风格: 微信公众号风格 (wechat)
📊 字数: 3500字
✓ 质量检查: 通过

下一步建议:
- 调用 /illustration-generator 生成配图
- 调用 /wechat-article-formatter 格式化为微信HTML
```

---

## 风格转换

将已有文章转换为其他风格。

**使用：**
```bash
/document-writer convert article.md --to xiaohongshu
```

**转换流程：**

1. 读取原文章
2. 调用 `get_conversion_guide(from_style, to_style)` 获取转换指南
3. 按指南调整：
   - **长文→短文**：提取核心观点，压缩为要点
   - **短文→长文**：扩展论述，添加案例和数据
4. 按目标风格规范重写
5. 质量自检
6. 保存输出

---

## 与其他 Skill 配合

| 顺序 | Skill | 功能 |
|------|-------|------|
| 1 | **document-writer** | 生成 Markdown 文章 |
| 2 | illustration-generator | 为文章生成配图 |
| 3 | md-to-pdf | 转换为 PDF |
| 4 | wechat-article-formatter | 格式化为微信 HTML |
| 5 | wechat-publisher | 发布到微信公众号 |

---

## shared-lib 接口参考

**模块路径：** `~/.claude/skills/shared-lib/writing/`

| 函数 | 用途 |
|------|------|
| `list_styles()` | 返回可用风格列表 |
| `get_style_info(style)` | 返回风格详情（字数、特点等） |
| `get_style_prompt(style)` | 返回完整风格指南（给 Claude 用） |
| `get_conversion_guide(from, to)` | 返回风格转换指南 |

**注意：** 内容类型判断由 Claude 完成，不依赖关键词匹配。

---

## 示例

### 示例1：写公众号文章

**用户：**
```
/document-writer "客家新论：秦军消失之谜" --style wechat
```

**Claude 执行：**
1. 读取主题
2. 使用 wechat 风格
3. 获取风格规范
4. 按规范撰写 3000-6000 字文章
5. 自检：短段落、加粗、互动结尾
6. 保存 `客家新论：秦军消失之谜.md`
7. 输出总结

### 示例2：从素材改写

**用户：**
```
/document-writer source.md --style xiaohongshu
```

**Claude 执行：**
1. 读取 source.md 内容
2. 使用 xiaohongshu 风格
3. 获取风格规范
4. 提取核心观点，压缩为 800-1200 字
5. 自检：情绪化、去爹味、emoji
6. 保存输出
7. 输出总结

### 示例3：风格转换

**用户：**
```
/document-writer convert long-article.md --to twitter
```

**Claude 执行：**
1. 读取长文
2. 获取转换指南（qiaomu → twitter）
3. 提取 3-5 个核心金句
4. 每条 100-280 字
5. 保存为推特线程格式
6. 输出总结
