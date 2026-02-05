# Shared Library 结构说明

## 最终结构

```
~/.claude/skills/shared-lib/
├── image_api.py          # 图像生成 API（独立）
└── video/                # 视频生成模块
    ├── __init__.py
    ├── tts/              # TTS 音频生成
    │   ├── __init__.py
    │   ├── base.py
    │   ├── edge_tts.py
    │   ├── indextts2.py
    │   ├── minimax.py
    │   ├── factory.py
    │   └── README.md
    └── animation/        # 文本动画
        ├── __init__.py
        └── animator.py
```

## 使用方式

### 1. 图像生成
```python
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from image_api import ImageGenerator
```

### 2. TTS 音频
```python
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from video.tts import TTSFactory

engine = TTSFactory.create('edge-tts')
```

### 3. 文本动画
```python
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from video.animation import TextAnimator

animator = TextAnimator(aspect_ratio='9:16')
```

### 4. 统一导入（推荐）
```python
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from video import TTSFactory, TextAnimator

# 使用
tts_engine = TTSFactory.create('edge-tts')
animator = TextAnimator(aspect_ratio='9:16')
```

## 已更新的 Skills

### 1. image-to-video
- ✅ `scripts/generate_tts_v2.py` - 使用 `video.tts`
- ✅ `scripts/compose_smart.py` - 使用 `video.animation`
- ✅ `TEXT_ANIMATION_README.md` - 更新文档

### 2. podcast-generator
- ✅ `tts_generator.py` - 使用 `video.tts`
- ✅ `example_shared_tts.py` - 更新示例

### 3. servasyy-document-interpreter
- ✅ 使用 `image_api`（未改动）

## 模块职责

### image_api.py
- 图像生成
- 支持多个 provider
- 独立模块

### video/tts/
- TTS 音频生成
- 支持 3 种引擎（Edge TTS, IndexTTS2, MiniMax）
- 统一接口

### video/animation/
- 文本动画生成
- 使用 Manim
- 支持 4 种动画风格
- 支持 16:9 和 9:16

## 优势

1. **逻辑清晰**：video 模块包含所有视频相关功能
2. **易于扩展**：以后可���添加 video.composer, video.effects 等
3. **命名空间明确**：避免命名冲突
4. **统一导入**：可以从 video 统一导入所有功能
