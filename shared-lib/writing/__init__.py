"""
写作风格系统
支持多种写作风格：乔木、小红书、Dankoe、微信公众号、Twitter

使用示例：
    from writing import (
        WritingStyleGenerator,
        list_styles,
        get_style_info,
        recommend_styles,
        get_style_prompt,
        analyze_content,
        get_conversion_guide
    )
    
    # 查看可用风格
    print(list_styles())  # ['qiaomu', 'xiaohongshu', 'dankoe', 'wechat', 'twitter']
    
    # 获取风格详情
    info = get_style_info('qiaomu')
    print(info['display_name'])  # 乔木风格
    
    # 根据内容推荐风格
    recs = recommend_styles("AI技术深度解读文章", top_n=3)
    for rec in recs:
        print(f"{rec['style']}: {rec['confidence']:.0%}")
    
    # 获取风格提示词（给LLM用）
    prompt = get_style_prompt('xiaohongshu')
    
    # 分析主题，获取写作建议（新增）
    analysis = analyze_content("AI Agent 技术教程")
    print(analysis['content_type'])       # 技术教程
    print(analysis['recommended_style'])  # qiaomu
    print(analysis['platform_fit'])       # {'微信公众号': 0.8, ...}
    
    # 风格转换指南（新增）
    guide = get_conversion_guide('qiaomu', 'xiaohongshu')
    print(guide['length_change'])    # 大幅压缩
    print(guide['key_adjustments'])  # ['提取核心观点...', ...]
    
风格说明：
    - qiaomu: 乔木风格，口语化深度解读
    - xiaohongshu: 小红书风格，情绪化短文
    - dankoe: Dankoe风格，挑衅式长文
    - wechat: 微信公众号风格，可读性强
    - twitter: Twitter/X风格，精炼有力
"""

from .generator import (
    WritingStyleGenerator,
    list_styles,
    get_style_info,
    recommend_styles,
    get_style_prompt,
    format_style_guide,
    analyze_content,
    get_conversion_guide,
)

__all__ = [
    'WritingStyleGenerator',
    'list_styles',
    'get_style_info',
    'recommend_styles',
    'get_style_prompt',
    'format_style_guide',
    'analyze_content',
    'get_conversion_guide',
]
