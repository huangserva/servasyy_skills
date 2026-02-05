"""
配图风格系统
支持 Style × Layout 二维组合
功能：3变体预览、自动分析配图位置、单图修改/添加/删除、小红书图片系列

使用示例：
    from illustration import (
        IllustrationGenerator, 
        list_styles, list_layouts, generate,
        recommend_styles, analyze_article,
        # 小红书专用
        XhsGenerator, analyze_xhs_content, generate_xhs_outline, recommend_xhs_styles
    )
    
    # 查看可用选项
    print(list_styles())   # 20种风格
    print(list_layouts())  # 5种布局
    
    # 3变体预览
    recommendations = recommend_styles("AI人工智能技术报告", detailed=True)
    
    # 自动分析配图位置
    analysis = analyze_article("article.md")
    
    # 小红书图片系列
    xhs_analysis = analyze_xhs_content("5个AI工具推荐")
    xhs_outline = generate_xhs_outline("内容...", style="notion", image_count=5)
    xhs_styles = recommend_xhs_styles("美妆护肤分享")

风格说明（20种）：
    基础风格：newyorker, ukiyoe, tech, notion, warm, flat, watercolor
    新增风格：elegant, minimal, playful, nature, sketch, vintage, 
             scientific, chalkboard, editorial, retro, blueprint, pixel-art, cute

布局说明（5种）：
    - single: 单一场景
    - infographic: 信息图
    - comparison: 对比图
    - flow: 流程图
    - scene: 场景图

小红书布局（6种）：
    - sparse: 稀疏布局（封面）
    - balanced: 平衡布局（常规）
    - dense: 密集布局（干货）
    - list: 列表布局（清单）
    - comparison: 对比布局
    - flow: 流程布局
"""

from .generator import (
    IllustrationGenerator,
    list_styles,
    list_layouts,
    generate,
)

from .xhs_generator import (
    XhsGenerator,
    analyze_xhs_content,
    generate_xhs_outline,
    recommend_xhs_styles,
)

# 便捷函数
def recommend_styles(content: str, top_n: int = 3, detailed: bool = False):
    """3变体预览：推荐风格"""
    gen = IllustrationGenerator()
    return gen.recommend_styles(content, top_n, detailed)

def analyze_article(markdown_path: str):
    """自动分析文章配图位置"""
    gen = IllustrationGenerator()
    return gen.analyze_article(markdown_path)

def generate_config(markdown_path: str, style: str = 'newyorker', output_path=None):
    """生成配图配置文件"""
    gen = IllustrationGenerator()
    return gen.generate_config(markdown_path, style, output_path)

__all__ = [
    # 通用配图
    'IllustrationGenerator',
    'list_styles',
    'list_layouts',
    'generate',
    'recommend_styles',
    'analyze_article',
    'generate_config',
    # 小红书专用
    'XhsGenerator',
    'analyze_xhs_content',
    'generate_xhs_outline',
    'recommend_xhs_styles',
]
