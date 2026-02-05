"""
图片动态效果模块（无需Manim）
使用ffmpeg实现各种动态效果
"""
import subprocess
import os


def create_dynamic_video_segment(
    text,
    audio_path,
    image_path,
    output_path,
    effect='ken_burns',
    width=1080,
    height=1920,
    font_size=60,
    max_chars_per_line=18,
    font_path="/System/Library/Fonts/PingFang.ttc"
):
    """
    创建带动态效果的视频片段
    
    Args:
        text: 字幕文本
        audio_path: 音频文件路径
        image_path: 背景图片路径
        output_path: 输出视频路径
        effect: 动态效果类型
            - 'ken_burns': 缩放+平移（推荐）
            - 'fade_in': 淡入
            - 'zoom_in': 放大
            - 'zoom_out': 缩小
            - 'slide_left': 向左滑动
            - 'slide_right': 向右滑动
            - 'none': 无动画（静态）
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
    
    # 创建字幕文件
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
    
    # 构建视频滤镜
    base_filter = f"scale={width}:{height},setsar=1"
    
    # 根据效果类型添加动画
    if effect == 'ken_burns':
        # Ken Burns: 缓慢缩放+平移
        animation_filter = (
            f"zoompan=z='min(zoom+0.0015,1.2)':d=1:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}"
        )
    elif effect == 'fade_in':
        # 淡入效果
        animation_filter = f"fade=t=in:st=0:d=1"
    elif effect == 'zoom_in':
        # 放大效果
        animation_filter = (
            f"zoompan=z='min(zoom+0.002,1.3)':d=1:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}"
        )
    elif effect == 'zoom_out':
        # 缩小效果
        animation_filter = (
            f"zoompan=z='if(lte(zoom,1.0),1.3,max(1.0,zoom-0.002))':d=1:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}"
        )
    elif effect == 'slide_left':
        # 向左滑动
        animation_filter = f"scroll=horizontal=-0.01"
    elif effect == 'slide_right':
        # 向右滑动
        animation_filter = f"scroll=horizontal=0.01"
    else:
        # 无动画
        animation_filter = ""
    
    # 组合滤镜
    if animation_filter:
        video_filter = f"{base_filter},{animation_filter}"
    else:
        video_filter = base_filter
    
    # 添加字幕
    subtitle_y = height - 300
    video_filter += (
        f",drawtext=fontfile={font_path}:textfile={textfile_path}:"
        f"fontsize={font_size}:fontcolor=white:borderw=4:bordercolor=black:"
        f"x=(w-text_w)/2:y={subtitle_y}"
    )
    
    # 生成视频
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', image_path,
        '-i', audio_path,
        '-vf', video_filter,
        '-t', str(duration),
        '-c:v', 'libx264', '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    
    # 清理临时文件
    if os.path.exists(textfile_path):
        os.remove(textfile_path)
    
    return os.path.exists(output_path) and os.path.getsize(output_path) > 0


# 效果说明
EFFECTS = {
    'ken_burns': '缓慢缩放+平移（最自然，推荐）',
    'fade_in': '淡入效果',
    'zoom_in': '放大效果',
    'zoom_out': '缩小效果',
    'slide_left': '向左滑动',
    'slide_right': '向右滑动',
    'none': '无动画（静态）'
}
