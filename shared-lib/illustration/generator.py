"""
配图风格生成器
支持 Style × Layout 二维组合系统
功能：3变体预览、自动分析配图位置、单图修改/添加/删除
"""
import re
import json
import yaml
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple


# 模块目录
MODULE_DIR = Path(__file__).parent
STYLES_DIR = MODULE_DIR / 'styles'
LAYOUTS_DIR = MODULE_DIR / 'layouts'


class IllustrationGenerator:
    """配图生成器，支持风格和布局组合"""
    
    def __init__(self, provider: str = 'auto'):
        """
        初始化生成器
        
        Args:
            provider: 图像API provider（传给底层 ImageGenerator）
        """
        self.provider = provider
        self._styles_cache: Dict[str, Dict] = {}
        self._layouts_cache: Dict[str, Dict] = {}
    
    def list_styles(self) -> List[str]:
        """列出所有可用风格"""
        return [f.stem for f in STYLES_DIR.glob('*.yaml')]
    
    def list_layouts(self) -> List[str]:
        """列出所有可用布局"""
        return [f.stem for f in LAYOUTS_DIR.glob('*.yaml')]
    
    def get_style_info(self, style: str) -> Optional[Dict[str, Any]]:
        """获取风格详情"""
        return self._load_style(style)
    
    def get_layout_info(self, layout: str) -> Optional[Dict[str, Any]]:
        """获取布局详情"""
        return self._load_layout(layout)
    
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
    
    def _load_layout(self, layout: str) -> Optional[Dict[str, Any]]:
        """加载布局配置"""
        if layout in self._layouts_cache:
            return self._layouts_cache[layout]
        
        layout_path = LAYOUTS_DIR / f'{layout}.yaml'
        if not layout_path.exists():
            print(f"⚠️ 布局不存在: {layout}")
            return None
        
        try:
            with open(layout_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self._layouts_cache[layout] = config
            return config
        except Exception as e:
            print(f"❌ 加载布局失败: {e}")
            return None
    
    def build_prompt(
        self,
        content: str,
        style: str = 'newyorker',
        layout: str = 'single',
        extra_instructions: str = ''
    ) -> str:
        """
        构建完整的图像生成提示词
        
        Args:
            content: 场景/内容描述
            style: 视觉风格
            layout: 布局类型
            extra_instructions: 额外指令
        
        Returns:
            组合后的完整prompt
        """
        style_config = self._load_style(style)
        layout_config = self._load_layout(layout)
        
        if not style_config:
            style_config = self._load_style('newyorker')
        if not layout_config:
            layout_config = self._load_layout('single')
        
        # 组合prompt
        parts = []
        
        # 1. 风格描述
        if style_config and 'prompt_template' in style_config:
            parts.append(style_config['prompt_template'].strip())
        
        # 2. 布局描述
        if layout_config and 'prompt_addition' in layout_config:
            parts.append(layout_config['prompt_addition'].strip())
        
        # 3. 内容描述
        parts.append(f"场景描述：{content}")
        
        # 4. 额外指令
        if extra_instructions:
            parts.append(f"额外要求：{extra_instructions}")
        
        return '\n\n'.join(parts)
    
    def generate(
        self,
        content: str,
        style: str = 'newyorker',
        layout: str = 'single',
        aspect_ratio: str = '16:9',
        output_path: Optional[str] = None,
        extra_instructions: str = '',
        max_retries: int = 2
    ) -> Tuple[str, str]:
        """
        生成配图
        
        Args:
            content: 场景/内容描述
            style: 视觉风格（newyorker/ukiyoe/tech/notion/warm/flat/watercolor）
            layout: 布局类型（single/infographic/comparison/flow/scene）
            aspect_ratio: 宽高比
            output_path: 输出路径（可选，如果提供则保存图片）
            extra_instructions: 额外指令
            max_retries: 最大重试次数
        
        Returns:
            (image_url, provider): 图片URL和使用的provider
        """
        # 构建完整prompt
        full_prompt = self.build_prompt(content, style, layout, extra_instructions)
        
        print(f"🎨 生成配图: style={style}, layout={layout}, aspect={aspect_ratio}")
        
        # 调用底层API
        import sys
        sys.path.insert(0, str(MODULE_DIR.parent))
        from image_api import ImageGenerator
        
        generator = ImageGenerator(provider=self.provider)
        
        try:
            image_url, used_provider = generator.generate_raw_style(
                prompt=full_prompt,
                aspect_ratio=aspect_ratio,
                max_retries=max_retries
            )
            
            # 保存图片（如果指定了输出路径）
            if output_path:
                generator.save_image(image_url, output_path)
                print(f"✅ 图片已保存: {output_path}")
            
            return (image_url, used_provider)
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            raise
    
    def recommend_style(self, content: str) -> List[Tuple[str, float]]:
        """
        根据内容推荐风格（简单版）
        
        Args:
            content: 内容描述
        
        Returns:
            [(style_name, score), ...] 按分数降序排列
        """
        # 关键词匹配
        keywords = {
            'tech': ['AI', '人工智能', '科技', '技术', '编程', '代码', '数据', '算法', '软件', '工具', '效率'],
            'notion': ['知识', '方法', '思维', '模型', '框架', '效率', '笔记', 'SaaS', '产品'],
            'warm': ['生活', '情感', '故事', '成长', '心理', '家庭', '亲子', '美食', '日常'],
            'newyorker': ['社会', '人文', '评论', '观点', '文化', '深度', '分析', '随笔'],
            'ukiyoe': ['历史', '古代', '传统', '东方', '日本', '中国', '古典', '文学'],
            'flat': ['商业', '产品', '企业', '报告', '培训', '流程', '介绍'],
            'watercolor': ['艺术', '旅行', '自然', '风景', '文学', '诗意', '浪漫']
        }
        
        scores = {}
        content_lower = content.lower()
        
        for style, kws in keywords.items():
            score = sum(1 for kw in kws if kw.lower() in content_lower)
            scores[style] = score
        
        # 如果没有匹配，给默认风格一个基础分
        if all(s == 0 for s in scores.values()):
            scores['newyorker'] = 0.5
        
        # 排序返回
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores

    def recommend_styles(
        self,
        content: str,
        top_n: int = 3,
        detailed: bool = False
    ) -> List[Dict[str, Any]]:
        """
        3变体预览：推荐最适合的风格
        
        Args:
            content: 文章内容
            top_n: 返回前N个推荐
            detailed: 是否返回详细信息
        
        Returns:
            [{'style': str, 'layout': str, 'confidence': float, 'reason': str, ...}, ...]
        """
        # 关键词匹配评分
        keywords = {
            'tech': {
                'words': ['AI', '人工智能', '科技', '技术', '编程', '代码', '数据', '算法', '软件', '工具'],
                'layout': 'infographic'
            },
            'notion': {
                'words': ['知识', '方法', '思维', '模型', '框架', '效率', '笔记', 'SaaS', '产品', '教程'],
                'layout': 'infographic'
            },
            'warm': {
                'words': ['生活', '情感', '故事', '成长', '心理', '家庭', '亲子', '美食', '日常', '温暖'],
                'layout': 'scene'
            },
            'newyorker': {
                'words': ['社会', '人文', '评论', '观点', '文化', '深度', '分析', '随笔', '讽刺'],
                'layout': 'single'
            },
            'ukiyoe': {
                'words': ['历史', '古代', '传统', '东方', '日本', '中国', '古典', '文学', '朝代'],
                'layout': 'scene'
            },
            'flat': {
                'words': ['商业', '产品', '企业', '报告', '培训', '流程', '介绍', '步骤'],
                'layout': 'flow'
            },
            'watercolor': {
                'words': ['艺术', '旅行', '自然', '风景', '文学', '诗意', '浪漫', '美学'],
                'layout': 'single'
            },
            # 新增风格
            'elegant': {
                'words': ['高端', '奢侈', '专业', '商务', 'CEO', '领导力', '思想', '战略'],
                'layout': 'single'
            },
            'minimal': {
                'words': ['极简', '简约', '禅', '冥想', '正念', '哲学', '本质', '纯粹'],
                'layout': 'single'
            },
            'playful': {
                'words': ['有趣', '好玩', '入门', '新手', '轻松', '趣味', '小白', '简单'],
                'layout': 'infographic'
            },
            'nature': {
                'words': ['环保', '绿色', '有机', '健康', '养生', '自然', '生态', '可持续'],
                'layout': 'scene'
            },
            'sketch': {
                'words': ['创意', '想法', '草稿', '头脑风暴', '灵感', '设计', '构思', '原型'],
                'layout': 'single'
            },
            'vintage': {
                'words': ['复古', '怀旧', '经典', '传统', '历史', '传记', '回忆', '老'],
                'layout': 'scene'
            },
            'scientific': {
                'words': ['科学', '论文', '研究', '实验', '医学', '生物', '化学', '物理', '学术'],
                'layout': 'infographic'
            },
            'chalkboard': {
                'words': ['教育', '课程', '教学', '学习', '培训', '讲解', '老师', '学生'],
                'layout': 'infographic'
            },
            'editorial': {
                'words': ['新闻', '报道', '调查', '深度', '媒体', '杂志', '记者', '信息图'],
                'layout': 'infographic'
            },
            'retro': {
                'words': ['80年代', '90年代', '复古', '霓虹', '蒸汽波', '游戏', '音乐', '潮流'],
                'layout': 'single'
            },
            'blueprint': {
                'words': ['架构', '系统', '设计', '工程', '建筑', '技术', '蓝图', '原理'],
                'layout': 'flow'
            },
            'pixel-art': {
                'words': ['像素', '游戏', '8bit', '复古游戏', '开发者', '程序员', 'geek'],
                'layout': 'single'
            },
            'cute': {
                'words': ['可爱', '少女', '粉色', '甜美', '小红书', '美妆', '护肤', '穿搭', '仙女'],
                'layout': 'infographic'
            }
        }
        
        scores = {}
        content_lower = content.lower()
        
        for style, config in keywords.items():
            score = sum(1 for kw in config['words'] if kw.lower() in content_lower)
            scores[style] = {'score': score, 'layout': config['layout']}
        
        # 排序
        sorted_styles = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        results = []
        for style, info in sorted_styles[:top_n]:
            score = info['score']
            confidence = min(score / 5.0, 1.0) if score > 0 else 0.3
            
            # 生成推荐理由
            style_config = self._load_style(style)
            reason = self._generate_style_reason(style, content)
            
            result = {
                'style': style,
                'layout': info['layout'],
                'confidence': confidence,
                'reason': reason
            }
            
            if detailed and style_config:
                result['style_name'] = style_config.get('name', style)
                result['style_description'] = style_config.get('description', '')
                result['best_for'] = style_config.get('best_for', [])
                result['characteristics'] = style_config.get('characteristics', [])
                if 'colors' in style_config:
                    result['colors'] = style_config['colors']
            
            results.append(result)
        
        # 如果没有匹配，返回默认
        if not results or all(r['confidence'] < 0.1 for r in results):
            results = [
                {'style': 'newyorker', 'layout': 'single', 'confidence': 0.5, 'reason': '通用风格，适合大多数内容'},
                {'style': 'notion', 'layout': 'infographic', 'confidence': 0.4, 'reason': '极简手绘，知识分享'},
                {'style': 'flat', 'layout': 'flow', 'confidence': 0.4, 'reason': '扁平插画，商业通用'}
            ]
        
        return results
    
    def _generate_style_reason(self, style: str, content: str) -> str:
        """生成风格推荐理由"""
        reasons = {
            'tech': '科技/数据类内容',
            'notion': '知识分享/方法论',
            'warm': '生活/情感类内容',
            'newyorker': '人文/深度评论',
            'ukiyoe': '历史/东方文化',
            'flat': '商业/流程类内容',
            'watercolor': '艺术/自然类内容',
            # 新增风格
            'elegant': '高端商务/专业领域',
            'minimal': '极简主义/哲学思考',
            'playful': '入门教程/趣味内容',
            'nature': '环保健康/自然主题',
            'sketch': '创意想法/头脑风暴',
            'vintage': '复古怀旧/历史传记',
            'scientific': '学术研究/科学论文',
            'chalkboard': '教育培训/课程讲解',
            'editorial': '新闻报道/信息图表',
            'retro': '复古潮流/娱乐文化',
            'blueprint': '系统架构/技术设计',
            'pixel-art': '游戏开发/程序员向',
            'cute': '小红书/可爱甜美风'
        }
        return reasons.get(style, '通用风格')

    def analyze_article(self, markdown_path: str) -> Dict[str, Any]:
        """
        自动分析文章，识别需要配图的位置
        
        Args:
            markdown_path: Markdown文件路径
        
        Returns:
            {
                'title': str,
                'cover': {'position': 0, 'content': str},
                'illustrations': [
                    {'position': int, 'h2_title': str, 'content': str, 'suggested_layout': str},
                    ...
                ]
            }
        """
        md_path = Path(markdown_path)
        if not md_path.exists():
            raise FileNotFoundError(f"文件不存在: {markdown_path}")
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # 提取标题
        title = ""
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # 分析章节
        illustrations = []
        current_h2 = None
        current_content = []
        h2_count = 0
        
        for i, line in enumerate(lines):
            if line.startswith('## '):
                # 保存上一个章节
                if current_h2:
                    section_content = '\n'.join(current_content)
                    suggested_layout = self._suggest_layout(section_content)
                    illustrations.append({
                        'position': h2_count,
                        'h2_title': current_h2,
                        'content': section_content[:500],  # 截取前500字
                        'suggested_layout': suggested_layout
                    })
                
                current_h2 = line[3:].strip()
                current_content = []
                h2_count += 1
            elif current_h2:
                current_content.append(line)
        
        # 保存最后一个章节
        if current_h2:
            section_content = '\n'.join(current_content)
            suggested_layout = self._suggest_layout(section_content)
            illustrations.append({
                'position': h2_count,
                'h2_title': current_h2,
                'content': section_content[:500],
                'suggested_layout': suggested_layout
            })
        
        return {
            'title': title,
            'cover': {
                'position': 0,
                'content': title
            },
            'illustrations': illustrations
        }
    
    def _suggest_layout(self, content: str) -> str:
        """根据内容建议布局"""
        content_lower = content.lower()
        
        # 检测布局信号
        if any(kw in content_lower for kw in ['步骤', '流程', '第一', '第二', '首先', '然后', '最后']):
            return 'flow'
        if any(kw in content_lower for kw in ['对比', '区别', '不同', 'vs', '优缺点']):
            return 'comparison'
        if any(kw in content_lower for kw in ['要点', '特点', '优势', '方法', '技巧', '原则']):
            return 'infographic'
        if any(kw in content_lower for kw in ['场景', '故事', '想象', '画面', '人物']):
            return 'scene'
        
        return 'single'
    
    def generate_config(
        self,
        markdown_path: str,
        style: str = 'newyorker',
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成配图配置文件（visual_config.json）
        
        注意：此函数只输出章节结构和摘要，不生成具体视觉描述。
        具体的视觉描述应由 Claude 阅读内容后生成。
        
        Args:
            markdown_path: Markdown文件路径
            style: 视觉风格
            output_path: 输出路径（默认与md同目录）
        
        Returns:
            配置字典
        """
        analysis = self.analyze_article(markdown_path)
        
        config = {
            'article_title': analysis['title'],
            'style': style,
            'note': '请由 Claude 为每个章节生成具体的视觉描述，而非使用通用模板。',
            'cover': {
                'h2_title': '封面',
                'content_summary': analysis['title'],
                'layout': 'single',
                'visual_description': ''  # 由 Claude 填写
            },
            'sections': []
        }
        
        for ill in analysis['illustrations']:
            config['sections'].append({
                'h2_title': ill['h2_title'],
                'content_summary': ill['content'][:300],  # 章节摘要
                'layout': ill['suggested_layout'],
                'visual_description': ''  # 由 Claude 填写具体视觉场景描述
            })
        
        # 保存配置
        if output_path:
            config_path = Path(output_path)
        else:
            config_path = Path(markdown_path).parent / 'visual_config.json'
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 配置已保存: {config_path}")
        return config
    
    def regenerate_illustration(
        self,
        work_dir: str,
        image_name: str,
        new_content: Optional[str] = None,
        new_style: Optional[str] = None,
        new_layout: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        单图修改：重新生成指定配图
        
        Args:
            work_dir: 工作目录（包含 visual_config.json）
            image_name: 图片文件名（如 illustration_01.png）
            new_content: 新的内容描述（可选）
            new_style: 新的风格（可选）
            new_layout: 新的布局（可选）
        
        Returns:
            (image_url, provider)
        """
        work_path = Path(work_dir)
        config_path = work_path / 'visual_config.json'
        
        # 读取配置
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        # 解析图片索引
        match = re.match(r'illustration_(\d+)\.png', image_name)
        if not match:
            raise ValueError(f"无效的图片名称: {image_name}")
        
        idx = int(match.group(1)) - 1
        sections = config.get('sections', [])
        
        # 获取或更新配置
        if idx < len(sections):
            section = sections[idx]
            content = new_content or section.get('visual_description', '')
            style = new_style or config.get('style', 'newyorker')
            layout = new_layout or section.get('layout', 'single')
        else:
            content = new_content or '配图'
            style = new_style or 'newyorker'
            layout = new_layout or 'single'
        
        # 生成图片
        output_path = work_path / 'images' / 'illustrations' / image_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"🔄 重新生成: {image_name}")
        return self.generate(
            content=content,
            style=style,
            layout=layout,
            output_path=str(output_path)
        )
    
    def add_illustration(
        self,
        work_dir: str,
        position: int,
        content: str,
        style: Optional[str] = None,
        layout: str = 'single'
    ) -> Tuple[str, str]:
        """
        添加新配图
        
        Args:
            work_dir: 工作目录
            position: 插入位置（章节索引，从1开始）
            content: 配图内容描述
            style: 风格（可选，默认使用配置中的风格）
            layout: 布局
        
        Returns:
            (image_url, provider)
        """
        work_path = Path(work_dir)
        config_path = work_path / 'visual_config.json'
        
        # 读取配置
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {'sections': []}
        
        style = style or config.get('style', 'newyorker')
        
        # 添加到配置
        new_section = {
            'h2_title': f'新增配图_{position}',
            'visual_description': content,
            'layout': layout,
            'caption': ''
        }
        
        sections = config.get('sections', [])
        if position <= len(sections):
            sections.insert(position - 1, new_section)
        else:
            sections.append(new_section)
        
        config['sections'] = sections
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # 生成图片
        image_name = f"illustration_{position:02d}_new.png"
        output_path = work_path / 'images' / 'illustrations' / image_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"➕ 添加配图: {image_name}")
        return self.generate(
            content=content,
            style=style,
            layout=layout,
            output_path=str(output_path)
        )
    
    def remove_illustration(self, work_dir: str, image_name: str) -> bool:
        """
        删除配图
        
        Args:
            work_dir: 工作目录
            image_name: 图片文件名
        
        Returns:
            是否成功删除
        """
        work_path = Path(work_dir)
        image_path = work_path / 'images' / 'illustrations' / image_name
        
        if image_path.exists():
            image_path.unlink()
            print(f"🗑️ 已删除: {image_name}")
            return True
        else:
            print(f"⚠️ 文件不存在: {image_name}")
            return False


def list_styles() -> List[str]:
    """列出所有可用风格"""
    return IllustrationGenerator().list_styles()


def list_layouts() -> List[str]:
    """列出所有可用布局"""
    return IllustrationGenerator().list_layouts()


def generate(
    content: str,
    style: str = 'newyorker',
    layout: str = 'single',
    aspect_ratio: str = '16:9',
    output_path: Optional[str] = None,
    provider: str = 'auto'
) -> Tuple[str, str]:
    """
    便捷函数：生成配图
    
    Args:
        content: 场景/内容描述
        style: 视觉风格
        layout: 布局类型
        aspect_ratio: 宽高比
        output_path: 输出路径（可选）
        provider: API provider
    
    Returns:
        (image_url, provider)
    """
    gen = IllustrationGenerator(provider=provider)
    return gen.generate(
        content=content,
        style=style,
        layout=layout,
        aspect_ratio=aspect_ratio,
        output_path=output_path
    )


if __name__ == '__main__':
    # 测试
    gen = IllustrationGenerator()
    
    print("可用风格:", gen.list_styles())
    print("可用布局:", gen.list_layouts())
    
    # 测试prompt构建
    prompt = gen.build_prompt(
        content="一个程序员在深夜写代码",
        style="tech",
        layout="single"
    )
    print("\n生成的Prompt:")
    print(prompt)
