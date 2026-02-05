"""
字幕工具函数
"""

def wrap_text(text, max_chars_per_line=18):
    """
    自动换行：每max_chars_per_line个字符换一行
    
    Args:
        text: 原始文本
        max_chars_per_line: 每行最大字符数
        
    Returns:
        换行后的文本，用\\n分隔
    """
    lines = []
    current_line = ""
    
    for char in text:
        current_line += char
        if len(current_line) >= max_chars_per_line:
            lines.append(current_line)
            current_line = ""
    
    if current_line:
        lines.append(current_line)
    
    return "\\n".join(lines)


def escape_drawtext(text):
    """
    转义drawtext特殊字符
    
    Args:
        text: 原始文本
        
    Returns:
        转义后的文本
    """
    return text.replace("'", "'\\\\\\''").replace(":", "\\:")
