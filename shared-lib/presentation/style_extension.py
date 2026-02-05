"""
EXTEND 扩展机制
允许用户自定义 PPT 风格，不修改核心代码
"""

import yaml
from pathlib import Path
from typing import Dict, Optional, Any


class StyleExtension:
    """风格扩展管理器"""
    
    # 扩展路径（优先级顺序）
    EXTENSION_PATHS = [
        Path('.ppt-extensions'),           # 项目级（优先级最高）
        Path.home() / '.ppt-extensions',   # 用户级
    ]
    
    def __init__(self):
        """初始化扩展管理器"""
        self._extensions_cache: Dict[str, Dict] = {}
    
    def find_extension(self, style_name: str) -> Optional[Path]:
        """
        查找扩展风格文件
        
        Args:
            style_name: 风格名称
        
        Returns:
            扩展文件路径（如果存在）
        """
        for ext_dir in self.EXTENSION_PATHS:
            style_file = ext_dir / 'styles' / f'{style_name}.yaml'
            if style_file.exists():
                return style_file
        return None
    
    def load_extension(self, style_name: str) -> Optional[Dict[str, Any]]:
        """
        加载扩展风格配置
        
        Args:
            style_name: 风格名称
        
        Returns:
            扩展配置字典
        """
        # 检查缓存
        if style_name in self._extensions_cache:
            return self._extensions_cache[style_name]
        
        # 查找扩展文件
        ext_file = self.find_extension(style_name)
        if not ext_file:
            return None
        
        try:
            with open(ext_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 缓存
            self._extensions_cache[style_name] = config
            return config
        
        except Exception as e:
            print(f"⚠️  加载扩展风格失败 ({style_name}): {e}")
            return None
    
    def apply_extension(
        self,
        base_config: Dict[str, Any],
        extension_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        应用扩展（继承 + 覆盖）
        
        Args:
            base_config: 基础风格配置
            extension_config: 扩展配置
        
        Returns:
            合并后的配置
        """
        # 深拷贝基础配置
        merged = dict(base_config)
        
        # 应用扩展
        for key, value in extension_config.items():
            if key == 'prompt_template' and '{base_prompt}' in str(value):
                # 替换 {base_prompt} 占位符
                base_prompt = base_config.get('prompt_template', '')
                merged[key] = value.replace('{base_prompt}', base_prompt)
            else:
                # 直接覆盖
                merged[key] = value
        
        return merged
    
    def list_extensions(self) -> Dict[str, Path]:
        """
        列出所有可用扩展
        
        Returns:
            {style_name: file_path}
        """
        extensions = {}
        
        for ext_dir in self.EXTENSION_PATHS:
            styles_dir = ext_dir / 'styles'
            if styles_dir.exists():
                for style_file in styles_dir.glob('*.yaml'):
                    style_name = style_file.stem
                    if style_name not in extensions:
                        extensions[style_name] = style_file
        
        return extensions
    
    @staticmethod
    def create_extension_template(
        style_name: str,
        extends: str = 'apple',
        location: str = 'user'
    ) -> Path:
        """
        创建扩展模板
        
        Args:
            style_name: 新风格名称
            extends: 继承的基础风格
            location: 'user' 或 'project'
        
        Returns:
            创建的扩展文件路径
        """
        # 确定位置
        if location == 'project':
            ext_dir = Path('.ppt-extensions')
        else:
            ext_dir = Path.home() / '.ppt-extensions'
        
        # 创建目录
        styles_dir = ext_dir / 'styles'
        styles_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成模板
        template = f"""# 自定义风格: {style_name}
name: {style_name}
extends: {extends}
display_name: {style_name.replace('_', ' ').title()}
description: 自定义风格，基于 {extends}

# 提示词模板（继承基础风格 + 自定义覆盖）
prompt_template: |
  {{base_prompt}}  # 继承 {extends} 的基础 prompt
  
  [CUSTOM OVERRIDE]:
  # 在这里添加你的自定义指令
  - Custom Color: #YOUR_COLOR
  - Custom Font: Your Font Name
  - Custom Element: Your custom requirements
  
  [ADDITIONAL RULES]:
  ✅ Your custom rules here
  ❌ Things to avoid

# 特性标签
characteristics:
  - 自定义特性1
  - 自定义特性2

# 最佳适用场景
best_for:
  - 你的使用场景1
  - 你的使用场景2

# 推荐关键词
keywords:
  - 关键词1
  - 关键词2
"""
        
        # 保存模板
        ext_file = styles_dir / f'{style_name}.yaml'
        with open(ext_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"✅ 扩展模板已创建: {ext_file}")
        print(f"\n请编辑此文件以自定义你的风格")
        
        return ext_file


# 便捷函数

def create_custom_style(
    style_name: str,
    extends: str = 'apple',
    location: str = 'user'
) -> Path:
    """
    创建自定义风格模板
    
    Args:
        style_name: 风格名称（如 'my_brand'）
        extends: 继承的基础风格（默认 'apple'）
        location: 'user' 或 'project'
    
    Returns:
        创建的模板文件路径
    
    Examples:
        >>> create_custom_style('company_brand', extends='apple', location='user')
        ✅ 扩展模板已创建: ~/.ppt-extensions/styles/company_brand.yaml
    """
    return StyleExtension.create_extension_template(style_name, extends, location)


def list_custom_styles() -> Dict[str, Path]:
    """列出所有自定义风格"""
    return StyleExtension().list_extensions()


if __name__ == '__main__':
    print("=" * 60)
    print("EXTEND 扩展机制")
    print("=" * 60)
    
    # 示例：创建自定义风格
    print("\n示例：创建自定义风格")
    print(">>> create_custom_style('my_brand', extends='apple')")
    print("\n这将创建模板文件，你可以编辑它来定义自己的品牌风格")
    
    # 列出现有扩展
    print("\n可用扩展:")
    extensions = list_custom_styles()
    if extensions:
        for name, path in extensions.items():
            print(f"  ✓ {name}: {path}")
    else:
        print("  (暂无自定义扩展)")
