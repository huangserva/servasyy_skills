"""
PPT生成系统
支持 Style × Theme × Layout 三维组合

使用示例：
    from presentation import (
        PresentationGenerator, StyleSelector,
        list_styles, list_layouts, list_themes
    )
    
    # 查看可用选项
    print(list_styles())   # 22 种风格
    print(list_layouts())  # 15 种布局
    print(list_themes())   # 8 种主题（仅 apple 风格）
    
    # 生成PPT幻灯片（风格由 AI 根据 SKILL.md 选择）
    gen = PresentationGenerator(style='vintage')
    
    # 生成封面
    image_url, provider = gen.generate_slide(
        layout='cover',
        content='中国古代历史'
    )

风格选择：
    由 AI 根据 ppt-generator/SKILL.md 中的评分表选择，不使用 Python 推荐函数。

布局说明：
    - cover: 封面页
    - section_divider: 章节分隔页
    - content_left: 左对齐内容页
    - content_center: 居中强调页
    - content_two_column: 双栏内容页
    - 更多布局见 SKILL.md

主题说明（仅apple风格）：
    - soft_blue: 柔和蓝（科技/商业）
    - elegant_purple: 优雅紫（创意/设计）
    - fresh_green: 清新绿（健康/环保）
    - warm_orange: 温暖橙（活力/社交）
    - rose_pink: 玫瑰粉（生活/美容）
    - cool_teal: 清凉青（金融/信任）
    - deep_indigo: 深邃靛（企业/权威）
    - neutral_grey: 中性灰（通用/极简）
"""

from .generator import (
    PresentationGenerator,
    list_styles,
    list_layouts,
    list_themes,
)

from .style_selector import (
    StyleSelector,
    get_style_info,
    get_theme_info,
)

from .session_manager import (
    SessionManager,
    create_session,
    load_session,
    list_recent_sessions,
)

from .exporter import (
    Exporter,
    export_to_pptx,
    export_to_pdf,
    export_both,
)

__all__ = [
    # 生成器
    'PresentationGenerator',
    'list_styles',
    'list_layouts',
    'list_themes',
    # 风格工具
    'StyleSelector',
    'get_style_info',
    'get_theme_info',
    # 会话管理
    'SessionManager',
    'create_session',
    'load_session',
    'list_recent_sessions',
    # 导出
    'Exporter',
    'export_to_pptx',
    'export_to_pdf',
    'export_both',
]
