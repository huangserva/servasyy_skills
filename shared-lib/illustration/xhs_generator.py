"""
小红书信息图生成器
支持 Style × Layout 二维组合，多图系列生成
"""
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

MODULE_DIR = Path(__file__).parent
XHS_DIR = MODULE_DIR / 'xhs'


class XhsGenerator:
    """小红书信息图生成器"""
    
    # 小红书专用风格推荐
    XHS_STYLES = {
        'cute': {
            'words': ['可爱', '少女', '粉色', '甜美', '美妆', '护肤', '穿搭', '仙女', '好物'],
            'description': '可爱甜美，少女心'
        },
        'notion': {
            'words': ['知识', '干货', '方法', '效率', '工具', '教程', '技巧', '分享'],
            'description': '极简知识卡片'
        },
        'tech': {
            'words': ['AI', '科技', '软件', 'App', '数码', '程序', '代码', '互联网'],
            'description': '科技数码风'
        },
        'warm': {
            'words': ['生活', '日常', '美食', '家居', '情感', '故事', '治愈', '温暖'],
            'description': '温暖生活风'
        },
        'playful': {
            'words': ['有趣', '好玩', '入门', '新手', '简单', '轻松', '趣味'],
            'description': '活泼有趣风'
        },
        'minimal': {
            'words': ['极简', '简约', '高级', '质感', '格调', '品味'],
            'description': '极简高级风'
        },
        'retro': {
            'words': ['复古', '怀旧', '潮流', '港风', '老照片', '经典'],
            'description': '复古潮流风'
        },
        'fresh': {
            'words': ['清新', '自然', '健康', '有机', '绿色', '森系'],
            'description': '清新自然风'
        },
        'bold': {
            'words': ['重要', '必看', '警告', '避坑', '注意', '震惊'],
            'description': '醒目警示风'
        }
    }
    
    # 内容类型映射
    CONTENT_TYPE_MAP = {
        '种草安利': {'style': 'cute', 'layout': 'balanced'},
        '干货分享': {'style': 'notion', 'layout': 'dense'},
        '测评对比': {'style': 'tech', 'layout': 'comparison'},
        '教程步骤': {'style': 'playful', 'layout': 'flow'},
        '避坑指南': {'style': 'bold', 'layout': 'list'},
        '清单合集': {'style': 'minimal', 'layout': 'list'},
        '个人故事': {'style': 'warm', 'layout': 'balanced'},
    }
    
    # Hook 类型
    HOOK_TYPES = {
        '数字钩子': ['5个方法', '3分钟学会', '99%的人不知道', '10个技巧'],
        '痛点钩子': ['踩过的坑', '后悔没早知道', '别再...', '千万不要'],
        '好奇钩子': ['原来...', '竟然...', '没想到...', '真相是'],
        '利益钩子': ['省钱', '变美', '效率翻倍', '免费', '白嫖'],
        '身份钩子': ['打工人必看', '学生党', '新手妈妈', '程序员']
    }
    
    def __init__(self, provider: str = 'auto'):
        self.provider = provider
        self._layouts_cache: Dict[str, Dict] = {}
    
    def list_xhs_layouts(self) -> List[str]:
        """列出小红书专用布局"""
        return [f.stem.replace('layout_', '') for f in XHS_DIR.glob('layout_*.yaml')]
    
    def _load_xhs_layout(self, layout: str) -> Optional[Dict[str, Any]]:
        """加载小红书布局配置"""
        if layout in self._layouts_cache:
            return self._layouts_cache[layout]
        
        layout_path = XHS_DIR / f'layout_{layout}.yaml'
        if not layout_path.exists():
            return None
        
        with open(layout_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        self._layouts_cache[layout] = config
        return config
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """
        分析内容，推荐风格和布局
        
        Returns:
            {
                'content_type': str,
                'recommended_style': str,
                'recommended_layout': str,
                'hook_type': str,
                'hook_suggestions': list,
                'image_count': int,
                'target_audience': list
            }
        """
        content_lower = content.lower()
        
        # 检测内容类型
        content_type = '干货分享'  # 默认
        type_scores = {}
        
        type_keywords = {
            '种草安利': ['推荐', '安利', '好物', '必买', '回购'],
            '干货分享': ['方法', '技巧', '教程', '分享', '干货'],
            '测评对比': ['测评', '对比', '评测', '优缺点', 'vs'],
            '教程步骤': ['步骤', '教程', '怎么', '如何', '操作'],
            '避坑指南': ['避坑', '踩坑', '别买', '千万不要', '警告'],
            '清单合集': ['清单', '合集', '整理', '汇总', 'TOP'],
            '个人故事': ['我的', '经历', '故事', '分享', '感受']
        }
        
        for ctype, keywords in type_keywords.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            type_scores[ctype] = score
        
        if type_scores:
            content_type = max(type_scores, key=type_scores.get)
        
        # 获取推荐风格和布局
        type_config = self.CONTENT_TYPE_MAP.get(content_type, {'style': 'notion', 'layout': 'balanced'})
        
        # 检测 Hook 类型
        hook_type = '数字钩子'  # 默认
        for htype, examples in self.HOOK_TYPES.items():
            if any(ex in content_lower for ex in examples):
                hook_type = htype
                break
        
        # 估算图片数量
        content_len = len(content)
        if content_len < 500:
            image_count = 3
        elif content_len < 1500:
            image_count = 5
        elif content_len < 3000:
            image_count = 7
        else:
            image_count = 9
        
        # 目标受众
        audience = []
        audience_keywords = {
            '学生党': ['学生', '校园', '省钱', '宿舍'],
            '打工人': ['打工', '职场', '效率', '摸鱼', '加班'],
            '宝妈': ['宝宝', '育儿', '亲子', '母婴'],
            '美妆爱好者': ['美妆', '护肤', '化妆', '彩妆'],
            '数码爱好者': ['数码', '科技', 'AI', '软件', 'App']
        }
        for aud, keywords in audience_keywords.items():
            if any(kw in content_lower for kw in keywords):
                audience.append(aud)
        
        if not audience:
            audience = ['通用受众']
        
        return {
            'content_type': content_type,
            'recommended_style': type_config['style'],
            'recommended_layout': type_config['layout'],
            'hook_type': hook_type,
            'hook_suggestions': self.HOOK_TYPES.get(hook_type, [])[:3],
            'image_count': image_count,
            'target_audience': audience
        }
    
    def generate_outline(
        self,
        content: str,
        style: str = 'notion',
        default_layout: str = 'balanced',
        image_count: int = 5
    ) -> Dict[str, Any]:
        """
        生成小红书图片系列大纲
        
        Returns:
            {
                'title': str,
                'style': str,
                'images': [
                    {'position': str, 'layout': str, 'core_message': str, 'visual_concept': str},
                    ...
                ]
            }
        """
        # 分析内容
        analysis = self.analyze_content(content)
        
        # 提取标题（第一行或前20字）
        lines = content.strip().split('\n')
        title = lines[0][:30] if lines else '小红书信息图'
        
        # 设计 Swipe Flow
        images = []
        
        # 第1张：封面
        images.append({
            'position': 'cover',
            'index': 1,
            'layout': 'sparse',
            'core_message': f'封面：{title}',
            'visual_concept': f'醒目标题，{style}风格，视觉冲击力强',
            'swipe_hook': '👇 往下看'
        })
        
        # 中间内容页
        content_count = image_count - 2  # 减去封面和结尾
        for i in range(content_count):
            images.append({
                'position': 'content',
                'index': i + 2,
                'layout': default_layout,
                'core_message': f'内容页 {i+1}',
                'visual_concept': f'{style}风格，{default_layout}布局',
                'swipe_hook': f'继续往下看 👇' if i < content_count - 1 else '最后一页 👇'
            })
        
        # 最后一张：结尾
        images.append({
            'position': 'ending',
            'index': image_count,
            'layout': 'sparse',
            'core_message': '总结 + 互动引导',
            'visual_concept': f'简洁收尾，互动引导，{style}风格',
            'swipe_hook': '💬 评论区见'
        })
        
        return {
            'title': title,
            'style': style,
            'analysis': analysis,
            'images': images
        }
    
    def recommend_styles(
        self,
        content: str,
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        推荐小红书适合的风格
        """
        content_lower = content.lower()
        scores = {}
        
        for style, config in self.XHS_STYLES.items():
            score = sum(1 for kw in config['words'] if kw in content_lower)
            scores[style] = {
                'score': score,
                'description': config['description']
            }
        
        sorted_styles = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        results = []
        for style, info in sorted_styles[:top_n]:
            confidence = min(info['score'] / 4.0, 1.0) if info['score'] > 0 else 0.3
            results.append({
                'style': style,
                'confidence': confidence,
                'description': info['description']
            })
        
        # 默认推荐
        if not results or all(r['confidence'] < 0.1 for r in results):
            results = [
                {'style': 'notion', 'confidence': 0.5, 'description': '极简知识卡片'},
                {'style': 'cute', 'confidence': 0.4, 'description': '可爱甜美风'},
                {'style': 'warm', 'confidence': 0.3, 'description': '温暖生活风'}
            ]
        
        return results


# 便捷函数
def analyze_xhs_content(content: str) -> Dict[str, Any]:
    """分析小红书内容"""
    return XhsGenerator().analyze_content(content)


def generate_xhs_outline(
    content: str,
    style: str = 'notion',
    layout: str = 'balanced',
    image_count: int = 5
) -> Dict[str, Any]:
    """生成小红书图片大纲"""
    return XhsGenerator().generate_outline(content, style, layout, image_count)


def recommend_xhs_styles(content: str, top_n: int = 3) -> List[Dict[str, Any]]:
    """推荐小红书风格"""
    return XhsGenerator().recommend_styles(content, top_n)
