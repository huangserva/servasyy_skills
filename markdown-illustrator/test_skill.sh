#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        🎨 Markdown Illustrator Skill - 快速测试             ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd ~/.claude/skills/markdown-illustrator

# 检查必要文件
echo "📋 检查Skill文件..."
files=("skill.md" "skill.prompt" "illustrate.py" "README.md" "config.yaml")
all_exist=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (缺失)"
        all_exist=false
    fi
done

echo ""

if [ "$all_exist" = true ]; then
    echo "✅ 所有必要文件都存在！"
else
    echo "❌ 部分文件缺失，请检查！"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Skill信息:"
echo "   名称: markdown-illustrator"
echo "   位置: ~/.claude/skills/markdown-illustrator/"
echo "   类型: Claude Skill with Python backend"
echo ""
echo "✨ 功能:"
echo "   • 智能分析Markdown文档结构"
echo "   • 为关键章节生成配图"
echo "   • 支持纽约客、浮世绘等风格"
echo "   • 灵活的图片生成路由"
echo "   • 自动插入图片到Markdown"
echo ""
echo "🚀 激活方式:"
echo "   在Claude对话中说:"
echo "   - '帮我给这篇文章配5张纽约客风格的图'"
echo "   - '用markdown-illustrator给我的文档配插图'"
echo "   - '用ModelScope给文章配图'"
echo ""
echo "💻 命令行测试:"
echo "   python3 illustrate.py <markdown_file> [options]"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Markdown Illustrator Skill 已就绪！"
echo ""
