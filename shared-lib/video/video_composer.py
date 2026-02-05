"""
视频合成工具
"""
import subprocess
import os
from .subtitle_utils import wrap_text, escape_drawtext


def create_video_segment(
    text,
    audio_path,
    image_path,
    output_path,
    width=1080,
    height=1920,
    font_size=60,
    max_chars_per_line=18,
    font_path="/System/Library/Fonts/PingFang.ttc"
):
    """
    创建单个视频片段（图片+音频+字幕）
    
    Args:
        text: 字幕文本
        audio_path: 音频文件路径
        image_path: 背景图片路径
        output_path: 输出视频路径
        width: 视频宽度
        height: 视频高度
        font_size: 字体大小
        max_chars_per_line: 每行最大字符数
        font_path: 字体文件路径
        
    Returns:
        bool: 是否成功
    """
    # 获取音频时长
    duration_cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
    ]
    result = subprocess.run(duration_cmd, capture_output=True, text=True)
    duration = float(result.stdout.strip())
    
    # 自动换行并写入textfile
    textfile_path = output_path + '.subtitle.txt'
    lines = []
    current = ""
    for char in text:
        current += char
        if len(current) >= max_chars_per_line:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    
    with open(textfile_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    # 计算字幕位置（底部留300像素）
    subtitle_y = height - 300
    
    # 使用textfile生成视频
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', image_path,
        '-i', audio_path,
        '-vf', (
            f"scale={width}:{height},setsar=1,"
            f"drawtext=fontfile={font_path}:textfile={textfile_path}:"
            f"fontsize={font_size}:fontcolor=white:borderw=4:bordercolor=black:"
            f"x=(w-text_w)/2:y={subtitle_y}"
        ),
        '-t', str(duration),
        '-c:v', 'libx264', '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    
    # 清理临时textfile
    if os.path.exists(textfile_path):
        os.remove(textfile_path)
    
    return os.path.exists(output_path) and os.path.getsize(output_path) > 0


def merge_video_segments(segment_files, output_path):
    """
    合并多个视频片段
    
    Args:
        segment_files: 视频片段文件列表
        output_path: 输出文件路径
        
    Returns:
        bool: 是否成功
    """
    if not segment_files:
        return False
    
    # 创建concat文件
    concat_file = output_path + '.concat.txt'
    with open(concat_file, 'w') as f:
        for seg_file in segment_files:
            f.write(f"file '{os.path.abspath(seg_file)}'\n")
    
    # 合并
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c', 'copy',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    
    # 清理临时文件
    if os.path.exists(concat_file):
        os.remove(concat_file)
    
    return os.path.exists(output_path) and os.path.getsize(output_path) > 0
