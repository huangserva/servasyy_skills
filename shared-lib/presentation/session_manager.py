"""
Session Manager
管理PPT生成会话，保持多页风格一致性
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import re


class SessionManager:
    """PPT生成会话管理器"""
    
    # 会话存储目录
    SESSIONS_DIR = Path.home() / '.claude/skills/shared-lib/presentation/.sessions'
    
    def __init__(self, session_id: Optional[str] = None):
        """
        初始化会话管理器
        
        Args:
            session_id: 会话ID（可选，不提供则自动生成）
        """
        self.sessions_dir = self.SESSIONS_DIR
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        if session_id:
            self.session_id = session_id
        else:
            self.session_id = self._generate_session_id()
        
        self.metadata_path = self.sessions_dir / f'{self.session_id}.json'
        self.metadata = self._load_metadata()
    
    @staticmethod
    def _generate_session_id() -> str:
        """生成唯一的会话ID"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        return f'ppt-{timestamp}'
    
    @staticmethod
    def generate_slug(title: str, max_length: int = 50) -> str:
        """
        生成 slug 命名（用于目录名）
        
        Args:
            title: 标题或主题
            max_length: 最大长度
        
        Returns:
            kebab-case 格式的 slug
        
        Examples:
            "Introduction to Machine Learning" -> "intro-machine-learning"
            "AI技术趋势报告 2024" -> "ai-tech-trend-report-2024"
        """
        # 转小写
        slug = title.lower()
        
        # 移除特殊字符，保留字母、数字、空格
        slug = re.sub(r'[^\w\s-]', '', slug)
        
        # 空格转连字符
        slug = re.sub(r'[\s_]+', '-', slug)
        
        # 移除连续的连字符
        slug = re.sub(r'-+', '-', slug)
        
        # 移除首尾连字符
        slug = slug.strip('-')
        
        # 截断到最大长度
        if len(slug) > max_length:
            slug = slug[:max_length].rstrip('-')
        
        # 如果为空，返回默认值
        if not slug:
            slug = 'presentation'
        
        return slug
    
    def create_output_directory(
        self,
        title: str,
        base_dir: Optional[Path] = None
    ) -> Path:
        """
        创建专业的输出目录结构（带 slug 命名）
        
        Args:
            title: PPT 标题
            base_dir: 基础目录（默认为 ~/slide-deck）
        
        Returns:
            创建的输出目录路径
        
        Examples:
            "AI技术趋势" -> ~/slide-deck/ai-tech-trend/
            如果已存在 -> ~/slide-deck/ai-tech-trend-20260123-183000/
        """
        if base_dir is None:
            base_dir = Path.home() / 'ppt-output'
        
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成 slug
        slug = self.generate_slug(title)
        target_dir = base_dir / slug
        
        # 如果目录已存在，添加时间戳
        if target_dir.exists():
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            slug_with_timestamp = f"{slug}-{timestamp}"
            target_dir = base_dir / slug_with_timestamp
        
        # 创建目录结构
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / 'prompts').mkdir(exist_ok=True)  # prompts 子目录
        
        return target_dir
    
    def save_metadata(
        self,
        style: str,
        theme: Optional[str] = None,
        language: str = 'zh',
        audience: str = 'general',
        title: str = '',
        output_dir: Optional[Path] = None,
        prompts: Optional[List[str]] = None,
        slug: Optional[str] = None  # 新增
    ):
        """
        保存会话元数据
        
        Args:
            style: 风格名称
            theme: 主题名称（可选）
            language: 语言代码
            audience: 目标受众
            title: PPT 标题
            output_dir: 输出目录
            prompts: 已生成的 prompts 列表
            slug: 目录 slug（可选）
        """
        self.metadata = {
            'session_id': self.session_id,
            'created_at': datetime.now().isoformat(),
            'style': style,
            'theme': theme,
            'language': language,
            'audience': audience,
            'title': title,
            'slug': slug or self.generate_slug(title) if title else None,
            'output_dir': str(output_dir) if output_dir else None,
            'prompts': prompts or [],
            'slide_count': len(prompts) if prompts else 0
        }
        
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """加载会话元数据"""
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取会话元数据"""
        return self.metadata
    
    def save_prompt_to_file(
        self,
        slide_number: int,
        prompt: str,
        output_dir: Optional[Path] = None,
        slide_title: str = ''
    ):
        """
        保存 prompt 到文件（Baoyu 风格）
        
        Args:
            slide_number: 幻灯片编号（从 1 开始）
            prompt: 生成 prompt 内容
            output_dir: 输出目录（如果为 None，使用 metadata 中的 output_dir）
            slide_title: 幻灯片标题（用于文件名）
        
        Examples:
            保存为: prompts/01-slide-cover.md
                   prompts/02-slide-intro.md
        """
        # 确定输出目录
        if output_dir is None:
            output_dir_str = self.metadata.get('output_dir')
            if not output_dir_str:
                raise ValueError("未设置 output_dir，无法保存 prompt")
            output_dir = Path(output_dir_str)
        
        # 创建 prompts 子目录
        prompts_dir = output_dir / 'prompts'
        prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        slide_num_str = f"{slide_number:02d}"
        
        if slide_title:
            # 使用标题生成 slug
            title_slug = self.generate_slug(slide_title, max_length=30)
            filename = f"{slide_num_str}-slide-{title_slug}.md"
        else:
            filename = f"{slide_num_str}-slide.md"
        
        # 保存 prompt
        prompt_file = prompts_dir / filename
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(f"# Slide {slide_number}")
            if slide_title:
                f.write(f": {slide_title}")
            f.write("\n\n")
            f.write(prompt)
        
        return prompt_file
    
    def add_prompt(self, slide_number: int, prompt: str, save_to_file: bool = False, slide_title: str = ''):
        """
        添加单个幻灯片的 prompt
        
        Args:
            slide_number: 幻灯片编号
            prompt: prompt 内容
            save_to_file: 是否保存到文件（默认 False，保持向后兼容）
            slide_title: 幻灯片标题（用于文件名）
        """
        if 'prompts' not in self.metadata:
            self.metadata['prompts'] = []
        
        # 确保列表足够长
        while len(self.metadata['prompts']) < slide_number:
            self.metadata['prompts'].append(None)
        
        # 插入 prompt（slide_number 从 1 开始）
        if slide_number <= len(self.metadata['prompts']):
            self.metadata['prompts'][slide_number - 1] = prompt
        else:
            self.metadata['prompts'].append(prompt)
        
        self.metadata['slide_count'] = len([p for p in self.metadata['prompts'] if p])
        
        # 保存更新
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        
        # 可选：保存到文件
        if save_to_file:
            try:
                self.save_prompt_to_file(slide_number, prompt, slide_title=slide_title)
            except Exception as e:
                print(f"⚠️  保存 prompt 文件失败: {e}")
    
    def get_prompt(self, slide_number: int) -> Optional[str]:
        """获取指定幻灯片的 prompt"""
        prompts = self.metadata.get('prompts', [])
        if 0 < slide_number <= len(prompts):
            return prompts[slide_number - 1]
        return None
    
    @classmethod
    def list_sessions(cls, recent: int = 10) -> List[Dict]:
        """
        列出最近的会话
        
        Args:
            recent: 返回最近N个会话
        
        Returns:
            会话元数据列表
        """
        sessions_dir = cls.SESSIONS_DIR
        if not sessions_dir.exists():
            return []
        
        sessions = []
        for session_file in sessions_dir.glob('*.json'):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                sessions.append(metadata)
            except Exception:
                continue
        
        # 按创建时间排序
        sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return sessions[:recent]
    
    @classmethod
    def load_session(cls, session_id: str) -> Optional['SessionManager']:
        """加载已存在的会话"""
        manager = cls(session_id=session_id)
        if manager.metadata:
            return manager
        return None
    
    def delete_session(self):
        """删除当前会话"""
        if self.metadata_path.exists():
            self.metadata_path.unlink()
    
    def __repr__(self) -> str:
        return f"SessionManager(session_id='{self.session_id}', style='{self.metadata.get('style')}', slides={self.metadata.get('slide_count', 0)})"


# 便捷函数

def create_session(
    title: str = '',
    style: str = 'apple',
    theme: Optional[str] = 'soft_blue',
    language: str = 'zh',
    audience: str = 'general'
) -> SessionManager:
    """
    创建新会话
    
    Returns:
        SessionManager 实例
    """
    session = SessionManager()
    session.save_metadata(
        style=style,
        theme=theme,
        language=language,
        audience=audience,
        title=title
    )
    return session


def load_session(session_id: str) -> Optional[SessionManager]:
    """加载已存在的会话"""
    return SessionManager.load_session(session_id)


def list_recent_sessions(recent: int = 10) -> List[Dict]:
    """列出最近的会话"""
    return SessionManager.list_sessions(recent=recent)


if __name__ == '__main__':
    # 测试
    print("=" * 60)
    print("Session Manager 测试")
    print("=" * 60)
    
    # 测试 slug 生成
    print("\n1. Slug 生成测试:")
    test_titles = [
        "Introduction to Machine Learning",
        "AI技术趋势报告 2024",
        "产品发布会 - 新功能介绍",
        "  Spaces  and   --  Dashes  "
    ]
    for title in test_titles:
        slug = SessionManager.generate_slug(title)
        print(f"   '{title}' -> '{slug}'")
    
    # 创建会话
    print("\n2. 创建会话:")
    session = create_session(
        title="AI技术趋势",
        style='blueprint',
        language='zh',
        audience='experts'
    )
    print(f"   ✅ 创建会话: {session.session_id}")
    
    # 添加 prompts
    print("\n3. 添加 prompts:")
    session.add_prompt(1, "封面页 prompt...")
    session.add_prompt(2, "第2页 prompt...")
    session.add_prompt(3, "第3页 prompt...")
    print(f"   ✅ 已添加 {session.metadata['slide_count']} 个 prompts")
    
    # 获取 prompt
    print("\n4. 获取 prompt:")
    prompt_2 = session.get_prompt(2)
    print(f"   第2页 prompt: {prompt_2}")
    
    # 列出最近会话
    print("\n5. 最近会话:")
    recent = list_recent_sessions(recent=5)
    for s in recent:
        print(f"   - {s['session_id']}: {s.get('title', 'N/A')} ({s.get('slide_count', 0)} slides)")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
