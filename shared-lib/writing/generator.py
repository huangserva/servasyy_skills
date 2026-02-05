"""
写作风格生成器
支持多种写作风格的选择、推荐和提示词生成
"""
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List


MODULE_DIR = Path(__file__).parent
STYLES_DIR = MODULE_DIR / 'styles'


class WritingStyleGenerator:
    """写作风格生成器"""
    
    def __init__(self):
        self._styles_cache: Dict[str, Dict] = {}
    
    def list_styles(self) -> List[str]:
        """列出所有可用风格"""
        return [f.stem for f in STYLES_DIR.glob('*.yaml')]
    
    def get_style_info(self, style: str) -> Optional[Dict[str, Any]]:
        """获取风格详情"""
        return self._load_style(style)
    
    def _load_style(self, style: str) -> Optional[Dict[str, Any]]:
        """加载风格配置"""
        if style in self._styles_cache:
            return self._styles_cache[style]
        
        style_path = STYLES_DIR / f'{style}.yaml'
        if not style_path.exists():
            print(f"⚠️ 风格不存在: {style}")
            return None
        
        try:
            with open(style_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self._styles_cache[style] = config
            return config
        except Exception as e:
            print(f"❌ 加载风格失败: {e}")
            return None
    
    def recommend_styles(
        self,
        content: str,
        top_n: int = 3,
        detailed: bool = False
    ) -> List[Dict[str, Any]]:
        """
        根据内容推荐写作风格
        
        Args:
            content: 内容描述或原文
            top_n: 返回前N个推荐
            detailed: 是否返回详细信息
        
        Returns:
            [{'style': str, 'confidence': float, 'reason': str, ...}, ...]
        """
        keywords = {
            'qiaomu': {
                'words': ['论文', '技术', '深度', '解读', '分析', '研究', 
                         '算法', '模型', '数据', '科学', '原理'],
                'length': 'long',
                'reason': '技术深度解读，适合复杂概念阐述'
            },
            'xiaohongshu': {
                'words': ['种草', '推荐', '好物', '测评', '避坑', '攻略',
                         '分享', '干货', '宝藏', '绝了', '安利'],
                'length': 'short',
                'reason': '小红书爆款，高互动短文'
            },
            'dankoe': {
                'words': ['思考', '认知', '成长', '哲学', '人生', '挑战',
                         '反思', '突破', '本质', '真相', '觉醒'],
                'length': 'long',
                'reason': '深度思考，反主流叙事'
            },
            'wechat': {
                'words': ['公众号', '微信', '文章', '报道', '分析', '观点',
                         '行业', '趋势', '深度', '长文'],
                'length': 'medium',
                'reason': '微信公众号长文，可读性强'
            },
            'twitter': {
                'words': ['推特', 'Twitter', 'X', '简短', '观点', '总结',
                         '要点', '精华', '干货', '线程'],
                'length': 'short',
                'reason': '社交媒体短文，精炼有力'
            }
        }
        
        scores = {}
        content_lower = content.lower()
        content_length = len(content)
        
        for style, config in keywords.items():
            # 关键词匹配
            word_score = sum(2 for kw in config['words'] if kw.lower() in content_lower)
            
            # 长度匹配
            length_score = 0
            if config['length'] == 'long' and content_length > 3000:
                length_score = 2
            elif config['length'] == 'medium' and 1000 < content_length <= 3000:
                length_score = 2
            elif config['length'] == 'short' and content_length <= 1000:
                length_score = 2
            
            scores[style] = {
                'score': word_score + length_score,
                'reason': config['reason']
            }
        
        # 排序
        sorted_styles = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        results = []
        for style, info in sorted_styles[:top_n]:
            score = info['score']
            confidence = min(score / 6.0, 1.0) if score > 0 else 0.3
            
            result = {
                'style': style,
                'confidence': confidence,
                'reason': info['reason']
            }
            
            if detailed:
                style_config = self._load_style(style)
                if style_config:
                    result['display_name'] = style_config.get('display_name', style)
                    result['description'] = style_config.get('description', '')
                    result['word_count'] = style_config.get('word_count', {})
                    result['best_for'] = style_config.get('best_for', [])
            
            results.append(result)
        
        # 默认推荐
        if not results or all(r['confidence'] < 0.1 for r in results):
            results = [
                {'style': 'qiaomu', 'confidence': 0.5, 'reason': '通用深度解读风格'},
                {'style': 'wechat', 'confidence': 0.4, 'reason': '公众号长文风格'},
                {'style': 'xiaohongshu', 'confidence': 0.3, 'reason': '短文种草风格'}
            ]
        
        return results
    
    def get_style_prompt(self, style: str) -> str:
        """
        获取风格提示词（给LLM用）
        
        Args:
            style: 风格名称
        
        Returns:
            完整的风格指导提示词
        """
        config = self._load_style(style)
        if not config:
            return ""
        
        return self.format_style_guide(config)
    
    def format_style_guide(self, config: Dict[str, Any]) -> str:
        """格式化风格配置为提示词"""
        parts = []
        
        # 基本信息
        parts.append(f"# {config.get('display_name', config.get('name', '写作风格'))}")
        parts.append(f"\n{config.get('description', '')}\n")
        
        # 核心特征
        if 'characteristics' in config:
            parts.append("## 核心特征")
            for char in config['characteristics']:
                parts.append(f"- {char}")
            parts.append("")
        
        # 适用场景
        if 'best_for' in config:
            parts.append("## 适用场景")
            for scene in config['best_for']:
                parts.append(f"- {scene}")
            parts.append("")
        
        # 字数要求
        if 'word_count' in config:
            wc = config['word_count']
            parts.append(f"## 字数要求：{wc.get('min', 0)}-{wc.get('max', 0)}字\n")
        
        # 结构要求
        if 'structure' in config:
            parts.append("## 结构要求")
            structure = config['structure']
            if isinstance(structure, dict):
                for key, value in structure.items():
                    if isinstance(value, str):
                        parts.append(f"- **{key}**：{value}")
                    elif isinstance(value, list):
                        parts.append(f"- **{key}**：")
                        for item in value:
                            parts.append(f"  - {item}")
            parts.append("")
        
        # 禁止使用
        if 'avoid' in config:
            parts.append("## 禁止使用")
            for item in config['avoid']:
                parts.append(f"- ❌ {item}")
            parts.append("")
        
        # 常用句式
        if 'phrases' in config:
            parts.append("## 常用句式")
            for phrase in config['phrases']:
                parts.append(f"- {phrase}")
            parts.append("")
        
        return '\n'.join(parts)
    
    def analyze_content(self, topic: str) -> Dict[str, Any]:
        """
        提供写作辅助信息（内容类型判断由 Claude 完成）
        
        注意：此函数不再自动判断内容类型，仅返回可用的风格列表和平台信息。
        内容类型、风格选择等决策应由 Claude 阅读内容后智能判断。
        
        Args:
            topic: 主题描述或内容大纲
        
        Returns:
            {
                'available_styles': list,  # 可用风格列表
                'platforms': list,          # 可发布平台
                'note': str                 # 使用说明
            }
        """
        return {
            'available_styles': self.list_styles(),
            'platforms': ['微信公众号', '小红书', 'Twitter/X', 'Newsletter', '知乎'],
            'note': '请由 Claude 阅读内容后判断内容类型，选择合适的写作风格和目标平台。不依赖关键词自动匹配。'
        }
    
    def _generate_key_points(self, content_type: str, topic: str) -> List[str]:
        """生成建议要点"""
        points_map = {
            '技术教程': [
                '从问题/痛点出发，说明为什么需要学这个',
                '循序渐进，从简单到复杂',
                '提供可运行的代码示例',
                '总结常见错误和解决方案'
            ],
            '技术解读': [
                '用通俗语言解释专业概念',
                '提供生活化类比帮助理解',
                '分析技术的优缺点和适用场景',
                '预测未来发展趋势'
            ],
            '产品评测': [
                '先给结论：推荐/不推荐',
                '列出优缺点对比',
                '说明适合什么人群',
                '给出替代方案'
            ],
            '观点输出': [
                '提出反常识或独特观点',
                '用案例/数据支撑观点',
                '回应可能的质疑',
                '给出行动建议'
            ],
            '经验分享': [
                '讲述真实经历和感受',
                '总结关键教训',
                '提供可复制的方法',
                '避免说教，多讲故事'
            ],
            '生活方式': [
                '用场景化描述引入',
                '图文并茂',
                '给出具体可操作的建议',
                '加入个人真实体验'
            ],
            '商业分析': [
                '用数据说话',
                '分析商业模式和竞争格局',
                '预测趋势和机会',
                '给出策略建议'
            ]
        }
        return points_map.get(content_type, [
            '明确核心观点',
            '提供支撑论据',
            '结构清晰',
            '结尾有行动号召'
        ])
    
    def get_conversion_guide(self, from_style: str, to_style: str) -> Dict[str, Any]:
        """
        获取风格转换指南
        
        Args:
            from_style: 原风格
            to_style: 目标风格
        
        Returns:
            {
                'from_style': str,
                'to_style': str,
                'length_change': str,      # 字数变化方向
                'key_adjustments': list,   # 主要调整点
                'conversion_prompt': str   # 转换提示词
            }
        """
        from_config = self._load_style(from_style)
        to_config = self._load_style(to_style)
        
        if not from_config or not to_config:
            return {'error': f'风格不存在: {from_style} 或 {to_style}'}
        
        # 字数变化
        from_max = from_config.get('word_count', {}).get('max', 5000)
        to_max = to_config.get('word_count', {}).get('max', 5000)
        
        if to_max < from_max * 0.5:
            length_change = '大幅压缩'
        elif to_max < from_max * 0.8:
            length_change = '适度压缩'
        elif to_max > from_max * 1.5:
            length_change = '大幅扩展'
        elif to_max > from_max * 1.2:
            length_change = '适度扩展'
        else:
            length_change = '基本保持'
        
        # 调整要点
        adjustments = self._get_conversion_adjustments(from_style, to_style)
        
        # 生成转换提示词
        to_word_count = to_config.get('word_count', {})
        conversion_prompt = f"""请将以下内容转换为 {to_config.get('display_name', to_style)} 风格。

目标风格要求：
{self.format_style_guide(to_config)}

转换要点：
{chr(10).join(f'- {adj}' for adj in adjustments)}

目标字数：{to_word_count.get('min', 1000)}-{to_word_count.get('max', 5000)}字

---
原文内容：
"""
        
        return {
            'from_style': from_style,
            'to_style': to_style,
            'length_change': length_change,
            'key_adjustments': adjustments,
            'conversion_prompt': conversion_prompt
        }
    
    def _get_conversion_adjustments(self, from_style: str, to_style: str) -> List[str]:
        """获取转换调整要点"""
        # 通用调整
        adjustments = []
        
        # 从长文到短文
        long_styles = ['qiaomu', 'dankoe']
        short_styles = ['xiaohongshu', 'twitter']
        
        if from_style in long_styles and to_style in short_styles:
            adjustments.extend([
                '提取核心观点，删除次要内容',
                '将长段落压缩为要点',
                '用金句代替详细论述',
                '保留最有冲击力的案例'
            ])
        
        # 从短文到长文
        if from_style in short_styles and to_style in long_styles:
            adjustments.extend([
                '扩展每个要点的详细论述',
                '添加案例和数据支撑',
                '增加背景知识介绍',
                '添加深度分析和思考'
            ])
        
        # 特定风格调整
        if to_style == 'xiaohongshu':
            adjustments.extend([
                '添加 emoji 表情',
                '使用口语化表达',
                '分段更短，多用空行',
                '标题加入数字和吸引词'
            ])
        
        if to_style == 'twitter':
            adjustments.extend([
                '每条控制在 280 字符内',
                '用线程(Thread)组织长内容',
                '每条开头要有吸引力',
                '结尾加入互动引导'
            ])
        
        if to_style == 'qiaomu':
            adjustments.extend([
                '使用对话式口语',
                '添加类比和比喻',
                '复杂概念用生活化例子解释',
                '保持"老朋友聊天"的语气'
            ])
        
        if to_style == 'dankoe':
            adjustments.extend([
                '使用短句，多换行',
                '观点要尖锐、反常识',
                '避免术语，用简单词汇',
                '结尾给出行动建议'
            ])
        
        if not adjustments:
            adjustments = [
                '调整语气和表达方式',
                '按目���风格调整结构',
                '适配目标字数要求'
            ]
        
        return adjustments


# 便捷函数
def list_styles() -> List[str]:
    """列出所有可用风格"""
    return WritingStyleGenerator().list_styles()


def get_style_info(style: str) -> Optional[Dict[str, Any]]:
    """获取风格详情"""
    return WritingStyleGenerator().get_style_info(style)


def recommend_styles(content: str, top_n: int = 3, detailed: bool = False) -> List[Dict[str, Any]]:
    """根据内容推荐写作风格"""
    return WritingStyleGenerator().recommend_styles(content, top_n, detailed)


def get_style_prompt(style: str) -> str:
    """获取风格提示词"""
    return WritingStyleGenerator().get_style_prompt(style)


def format_style_guide(config: Dict[str, Any]) -> str:
    """格式化风格配置"""
    return WritingStyleGenerator().format_style_guide(config)


def analyze_content(topic: str) -> Dict[str, Any]:
    """分析主题，返回写作建议"""
    return WritingStyleGenerator().analyze_content(topic)


def get_conversion_guide(from_style: str, to_style: str) -> Dict[str, Any]:
    """获取风格转换指南"""
    return WritingStyleGenerator().get_conversion_guide(from_style, to_style)


if __name__ == '__main__':
    gen = WritingStyleGenerator()
    
    print("可用风格:", gen.list_styles())
    print()
    
    # 测试推荐
    recs = gen.recommend_styles("AI技术深度解读文章，分析算法原理", detailed=True)
    print("风格推荐:")
    for rec in recs:
        print(f"  {rec['style']}: {rec['confidence']:.0%} - {rec['reason']}")
    print()
    
    # 测试提示词生成
    prompt = gen.get_style_prompt('qiaomu')
    print("乔木风格提示词:")
    print(prompt[:500] + "...")
