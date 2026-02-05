# Installation Guide

## Prerequisites

- Python 3.8+
- Access to at least one image generation provider

## Setup Steps

### 1. Verify Skill Installation

```bash
ls ~/.claude/skills/markdown-illustrator/
```

Should show:
- skill.md
- skill.json
- skill.prompt
- illustrate.py
- README.md
- config.yaml

### 2. Install Python Dependencies

```bash
pip3 install requests pillow --break-system-packages
```

### 3. Configure Providers

The skill uses `~/.claude/skills/shared-lib/image_api.py` which should already be configured.

Available providers:
- **modelscope** (Recommended) - Cloud, no local setup needed
- **google-local** - Requires local Gemini API service on port 8045
- **zimage** - Requires local ComfyUI service
- **volcengine** - Cloud, requires API key
- **apimart** - Cloud, requires API key

### 4. Test the Skill

```bash
cd ~/.claude/skills/markdown-illustrator
python3 illustrate.py --help
```

### 5. Quick Test

Create a test Markdown file:

```bash
cat > /tmp/test.md << 'TESTMD'
# Test Article

## Introduction
This is a test section.

## Main Content
This is another section.
TESTMD
```

Generate illustrations:

```bash
python3 illustrate.py /tmp/test.md --num 2 --priority modelscope
```

## Usage in Claude

Once installed, activate the skill in conversation:

```
"帮我用markdown-illustrator给这篇文章配5张纽约客风格的图"
```

or

```
"Use markdown-illustrator to generate 3 ukiyo-e style illustrations for my document"
```

## Troubleshooting

### Issue: "No module named 'image_api'"

**Solution**: Ensure `~/.claude/skills/shared-lib/image_api.py` exists

### Issue: "All providers failed"

**Solution**: 
1. Check network connection
2. Verify at least one provider is accessible
3. Try specifying a working provider: `--priority modelscope`

### Issue: "401 Unauthorized" for ModelScope

**Solution**: 
1. ModelScope requires Alibaba Cloud account binding
2. Complete real-name verification
3. Visit: https://www.modelscope.cn/my/accountsettings

## Configuration

Edit `config.yaml` to customize:
- Default style
- Default number of images
- Provider priorities
- Output templates

## Support

For issues or questions, refer to:
- README.md - Detailed usage guide
- skill.md - Skill description
- skill.prompt - Claude behavior guide
