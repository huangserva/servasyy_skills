# PPT 系统整合架构设计

> 融合我们的架构优势 + baoyu-slide-deck 的功能完整性

---

## 设计原则

1. **保留我们的核心架构**：Python 模块化、Layout 系统、主题变体、智能算法
2. **移植 baoyu 的优势功能**：16 种风格、Session ID、多语言、PDF 导出
3. **向后兼容**：保持现有 API 不变，新功能通过可选参数添加
4. **渐进增强**：分阶段实施，每个阶段都可独立使用

---

## 整合后的目录结构

```
~/.claude/skills/shared-lib/presentation/
├── __init__.py                 # 公共 API（扩展）
├── generator.py                # 生成器（增强）
├── style_selector.py           # 风格选择器（增强）
├── session_manager.py          # 新增：Session 管理
├── i18n.py                     # 新增：多语言支持
├── exporter.py                 # 新增：PDF/PPTX 导出
│
├── styles/                     # 风格库（22 种）
│   ├── apple.yaml              # 原有 6 种
│   ├── material.yaml
│   ├── fluent.yaml
│   ├── editorial.yaml
│   ├── storytelling.yaml
│   ├── neumorphism.yaml
│   ├── blueprint.yaml          # 新增 10 种（从 baoyu 移植）
│   ├── chalkboard.yaml
│   ├── notion.yaml
│   ├── bold_editorial.yaml
│   ├── corporate.yaml
│   ├── dark_atmospheric.yaml
│   ├── editorial_infographic.yaml
│   ├── fantasy_animation.yaml
│   ├── intuition_machine.yaml
│   ├── minimal.yaml
│   ├── pixel_art.yaml
│   ├── scientific.yaml
│   ├── sketch_notes.yaml
│   ├── vector_illustration.yaml
│   ├── vintage.yaml
│   └── watercolor.yaml
│
├── layouts/                    # 布局库（保持现有 5 种）
│   ├── cover.yaml
│   ├── section_divider.yaml
│   ├── content_left.yaml
│   ├── content_center.yaml
│   └── content_two_column.yaml
│
├── themes/                     # 主题库（保持现有 8 种）
│   ├── soft_blue.yaml
│   ├── elegant_purple.yaml
│   ├── fresh_green.yaml
│   ├── warm_orange.yaml
│   ├── rose_pink.yaml
│   ├── cool_teal.yaml
│   ├── deep_indigo.yaml
│   └── neutral_grey.yaml
│
└── extensions/                 # 新增：EXTEND 扩展机制
    └── README.md
```

---

## 统一的风格配置格式（YAML）

### 基础风格格式
```yaml
# styles/blueprint.yaml
name: blueprint
display_name: 技术蓝图
description: 精确的技术蓝图风格，专业分析性视觉呈现
category: technical  # 新增：风格分类

# 提示词模板（核心）
prompt_template: |
  16:9 landscape aspect ratio, BLUEPRINT STYLE with professional analytical visual presentation.
  
  [DESIGN AESTHETIC]:
  Clean, structured visual metaphors using blueprints, diagrams, and schematics.
  Precise, analytical and aesthetically refined.
  
  [BACKGROUND]:
  - Color: Blueprint Off-White (#FAF8F5)
  - Texture: Subtle grid overlay, light engineering paper feel
  
  [TYPOGRAPHY]:
  - Primary: Neue Haas Grotesk Display Pro (clean sans-serif)
  - Secondary: Tiempos Text (elegant serif)
  
  [COLOR PALETTE]:
  - Background: Blueprint Paper #FAF8F5
  - Primary Text: Deep Slate #334155
  - Primary Accent: Engineering Blue #2563EB
  
  [VISUAL ELEMENTS]:
  - Precise lines with consistent stroke weights
  - Technical schematics and clean vector graphics
  - Connection lines use straight lines or 90-degree angles only
  
  [KEY PRINCIPLES]:
  ✅ Maintain consistent line weights, grid alignment
  ❌ No hand-drawn shapes, curved lines, photographic elements

# 是否支持主题变体
supports_themes: false
default_theme: null

# 特性标签（用于推荐算法）
characteristics:
  - 技术精确
  - 网格对齐
  - 工程图纸
  - 结构化
  - 专业分析

# 最佳适用场景
best_for:
  - 技术架构
  - 系统设计
  - 数据分析
  - 工程文档
  - 流程图

# 推荐关键词（用于自动匹配）
keywords:
  - 架构
  - 系统
  - 技术
  - 分析
  - 工程
  - 流程
  - blueprint
  - architecture
  - system
  - technical

# 语言支持（新增）
language_notes:
  zh: 使用中文字体 PingFang SC
  en: 使用 Neue Haas Grotesk
  ja: 使用 Hiragino Sans

# 受众适配（新增）
audience_adjustments:
  beginners:
    complexity_level: low
    explanation_depth: high
  executives:
    complexity_level: medium
    visual_hierarchy: strong
  experts:
    complexity_level: high
    data_density: high
```

---

## 增强的 API 接口

### 1. PresentationGenerator（增强版）

```python
class PresentationGenerator:
    def __init__(
        self,
        style: str = 'apple',
        theme: Optional[str] = 'soft_blue',
        session_id: Optional[str] = None,      # 新增
        language: str = 'zh',                   # 新增
        audience: str = 'general',              # 新增
        provider: str = 'auto'
    ):
        """
        初始化生成器
        
        Args:
            style: 视觉风格（22 种可选）
            theme: 颜色主题（仅 apple 风格支持）
            session_id: 会话ID，保持多页风格一致（可选）
            language: 语言代码（zh/en/ja/...）
            audience: 目标受众（beginners/intermediate/experts/executives/general）
            provider: 图像API provider
        """
        
    def generate_slide(
        self,
        layout: str = 'cover',
        content: str = '',
        extra_instructions: str = '',
        save_prompt: bool = True,              # 新增：是否保存 prompt
        output_dir: Optional[Path] = None      # 新增：指定输出目录
    ) -> Tuple[str, str]:
        """
        生成单个幻灯片
        
        Returns:
            (image_url, provider_used)
        """
        
    def batch_generate_slides(
        self,
        slides_config: List[Dict],
        output_dir: Path,
        parallel: bool = True,
        max_workers: int = 3,
        slug: Optional[str] = None             # 新增：目录 slug 命名
    ) -> List[Dict]:
        """
        批量生成幻灯片（保留并行能力）
        
        Args:
            slug: 项目 slug（如 'intro-machine-learning'）
                 如果提供，输出到 output_dir/slide-deck/{slug}/
        """
```

### 2. StyleSelector（增强版）

```python
class StyleSelector:
    # 扩展关键词库（合并 baoyu 的信号词）
    KEYWORD_THEMES = {
        'tech': [...],
        'business': [...],
        'creative': [...],
        'education': [...],      # 新增：教育场景
        'gaming': [...],         # 新增：游戏场景
        'lifestyle': [...],
        'story': [...],
        'data': [...],
        'academic': [...]
    }
    
    # 扩展风格映射（22 种风格）
    THEME_STYLE_MAP = {
        'tech': [
            ('apple', 'soft_blue'),
            ('blueprint', None),         # 新增
            ('notion', None),            # 新增
            ('material', None)
        ],
        'education': [
            ('chalkboard', None),        # 新增
            ('sketch_notes', None),      # 新增
            ('apple', 'warm_orange')
        ],
        'gaming': [
            ('pixel_art', None),         # 新增
            ('dark_atmospheric', None),  # 新增
            ('fantasy_animation', None)  # 新增
        ],
        # ... 其他映射
    }
    
    def recommend_styles(
        self,
        content: str,
        title: str = "",
        top_n: int = 3,
        detailed: bool = False,
        language: str = 'zh',          # 新增
        audience: str = 'general'      # 新增
    ) -> List[Dict[str, Any]]:
        """
        智能推荐风格（融合两套算法）
        
        Returns:
            [{'style': str, 'theme': Optional[str], 
              'confidence': float, 'reason': str, ...}, ...]
        """
```

### 3. SessionManager（新增）

```python
class SessionManager:
    """
    管理生成会话，保持多页风格一致性
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.metadata = {}
        
    def save_metadata(
        self,
        style: str,
        theme: Optional[str],
        language: str,
        audience: str,
        prompts: List[str]
    ):
        """保存会话元数据"""
        
    def load_metadata(self) -> Dict:
        """加载会话元数据"""
        
    def generate_slug(self, title: str) -> str:
        """
        生成 slug 命名
        
        Example:
            "Introduction to Machine Learning" -> "intro-machine-learning"
        """
```

### 4. Exporter（新增）

```python
class Exporter:
    """
    导出器：支持 PPTX 和 PDF
    """
    @staticmethod
    def export_to_pptx(
        slides_dir: Path,
        output_path: Path,
        metadata: Optional[Dict] = None
    ):
        """导出为 PPTX（保留现有逻辑）"""
        
    @staticmethod
    def export_to_pdf(
        slides_dir: Path,
        output_path: Path,
        metadata: Optional[Dict] = None
    ):
        """
        导出为 PDF（新增）
        
        使用 img2pdf 或 PIL + reportlab
        """
```

---

## 兼容性保证

### 向后兼容
所有现有代码**无需修改**即可继续使用：

```python
# 旧代码（仍然有效）
gen = PresentationGenerator(style='apple', theme='soft_blue')
url, provider = gen.generate_slide(layout='cover', content='标题')
```

### 渐进增强
新功能通过**可选参数**使用：

```python
# 新代码（启用新功能）
gen = PresentationGenerator(
    style='blueprint',           # 使用新风格
    session_id='slides-20260122',  # 启用会话一致性
    language='zh',               # 指定语言
    audience='experts'           # 适配专家受众
)
```

---

## 扩展机制（EXTEND）

支持用户自定义风格和配置：

### 扩展路径（优先级顺序）
1. **项目级**：`./.ppt-extensions/styles/custom_style.yaml`
2. **用户级**：`~/.ppt-extensions/styles/custom_style.yaml`

### 扩展格式
```yaml
# ~/.ppt-extensions/styles/my_brand.yaml
name: my_brand
extends: apple  # 继承基础风格
display_name: 我的品牌风格

# 覆盖特定配置
prompt_template: |
  {base_prompt}  # 继承 apple 的基础 prompt
  
  [BRAND OVERRIDE]:
  - Brand Color: #FF6B35
  - Logo Position: Top Right
  
characteristics:
  - 品牌定制
  - 橙色主调

best_for:
  - 品牌宣传
  - 市场营销
```

---

## 实施阶段

### ✅ 阶段 1：风格库扩展（2-3 小时）
- [x] 编写 MD → YAML 转换脚本
- [ ] 移植 baoyu 的 10 种新风格
- [ ] 测试新风格生成效果

### ⏳ 阶段 2：核心功能增强（3-4 小时）
- [ ] 实现 SessionManager
- [ ] 添加 language 和 audience 参数支持
- [ ] 扩展 StyleSelector 推荐算法
- [ ] 实现 PDF 导出

### ⏳ 阶段 3：工作流优化（2-3 小时）
- [ ] Slug 命名和专业目录结构
- [ ] Prompts 保存机制
- [ ] EXTEND 扩展支持

### ⏳ 阶段 4：测试与文档（1-2 小时）
- [ ] 完整功能测试
- [ ] 更新 API 文档
- [ ] 编写使用示例

---

## 下一步行动

1. **审阅此架构设计**：你觉得这个方案如何？有需要调整的吗？
2. **确认后开始实施**：我会按照阶段 1 → 2 → 3 → 4 的顺序执行
3. **保持沟通**：每个阶段完成后给你汇报

---

## 预期成果

整合完成后，你将拥有：

✅ **22 种风格**（6 原有 + 16 新增）  
✅ **8 种颜色主题**（Apple 专属）  
✅ **5 种布局**（保留我们的优势）  
✅ **智能推荐算法**（融合两套）  
✅ **Session ID 一致性**（多页统一）  
✅ **多语言 + 受众适配**  
✅ **PDF + PPTX 导出**  
✅ **EXTEND 自定义扩展**  
✅ **向后兼容**（旧代码无需修改）  

🎯 **目标**：成为功能最完整的 PPT 生成系统！
