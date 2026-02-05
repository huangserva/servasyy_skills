"""
Manim文本动画视频合成
结合背景图片 + Manim文字动画 + 音频 + BGM

支持：
- 4种动画风格（write/typewriter/fade_in/slide_in）
- 3种视频尺寸（16:9/9:16/1:1）
- BGM背景音乐
- 透明背景叠加
"""
import subprocess
import os
import sys
sys.path.append(os.path.expanduser('~/.claude/skills/shared-lib'))

from video.animation.animator import TextAnimator

# 视频尺寸预设
VIDEO_SIZES = {
    '16:9': (1920, 1080),   # 横屏（B站、YouTube）
    '9:16': (1080, 1920),   # 竖屏（抖音、小红书）
    '1:1': (1080, 1080),    # 方形（小红书、Instagram）
}


def create_manim_video_segment(
    text,
    audio_path,
    image_path,
    output_path,
    animation_style='write',
    aspect_ratio='9:16',
    width=None,
    height=None,
    font_size=100,
    bgm_path=None,
    bgm_volume=0.3
):
    """
    创建带Manim文字动画的视频片段
    
    Args:
        text: 文本内容
        audio_path: 音频文件路径
        image_path: 背景图片路径
        output_path: 输出视频路径
        animation_style: Manim动画风格
            - 'write': 手写效果（推荐）
            - 'typewriter': 打字机效果
            - 'fade_in': 淡入
            - 'slide_in': 滑入
        aspect_ratio: 视频比例 ('16:9', '9:16', '1:1')
        width: 视频宽度（可选，默认从aspect_ratio推断）
        height: 视频高度（可选，默认从aspect_ratio推断）
        font_size: 字体大小
        bgm_path: BGM音乐路径（可选）
        bgm_volume: BGM音量 (0.0-1.0)
        
    Returns:
        bool: 是否成功
    """
    # 确定视频尺寸
    if width is None or height is None:
        if aspect_ratio in VIDEO_SIZES:
            width, height = VIDEO_SIZES[aspect_ratio]
        else:
            width, height = 1080, 1920  # 默认竖屏
    # 获取音频时长
    duration_cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
    ]
    result = subprocess.run(duration_cmd, capture_output=True, text=True)
    duration = float(result.stdout.strip())
    
    # 生成Manim文字动画
    aspect_ratio = '9:16' if height > width else '16:9'
    animator = TextAnimator(aspect_ratio=aspect_ratio)
    
    manim_temp = output_path + '.manim_temp.mp4'
    
    print(f"   🎨 生成Manim动画: {animation_style}...")
    success = animator.generate_text_animation(
        text=text,
        duration=duration,
        output_path=manim_temp,
        style=animation_style,
        font_size=font_size,
        color='WHITE',
        background_color='#00000000'  # 透明背景
    )
    
    # Manim会把文件放在自己的目录，找最新的.mov文件
    import glob
    import os
    
    # 搜索所有可能的临时目录
    search_paths = [
        '/private/tmp/**/videos/**/*.mov',
        '/tmp/**/videos/**/*.mov',
        '/private/tmp/**/*.mov',
        '/tmp/**/*.mov'
    ]
    
    manim_files = []
    for pattern in search_paths:
        manim_files = glob.glob(pattern, recursive=True)
        if manim_files:
            break
    
    if not manim_files:
        print(f"   ❌ Manim动画生成失败")
        return False
    
    actual_manim_path = max(manim_files, key=os.path.getmtime)  # 取最新的
    print(f"   ✅ Manim动画: {actual_manim_path}")
    
    # 合成：背景图 + Manim动画 + 音频
    print(f"   🎬 合成视频...")
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-t', str(duration), '-i', image_path,  # 背景图
        '-i', actual_manim_path,  # Manim动画（透明背景）
        '-i', audio_path,  # 音频
        '-filter_complex',
        f'[0:v]scale={width}:{height},setsar=1[bg];'
        f'[1:v]scale={width}:{height}[anim];'
        f'[bg][anim]overlay=(W-w)/2:(H-h)/2:format=auto',  # 支持alpha
        '-t', str(duration),
        '-c:v', 'libx264', '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    
    # 清理临时文件
    if os.path.exists(actual_manim_path):
        os.remove(actual_manim_path)
    
    # 检查视频是否生成成功
    video_created = os.path.exists(output_path) and os.path.getsize(output_path) > 0
    
    # 如果有BGM，添加背景音乐
    if video_created and bgm_path:
        from video.bgm import add_bgm_to_video
        
        temp_video = output_path + '.no_bgm.mp4'
        os.rename(output_path, temp_video)
        
        bgm_success = add_bgm_to_video(
            video_path=temp_video,
            bgm_path=bgm_path,
            output_path=output_path,
            bgm_volume=bgm_volume,
            loop=True,
            fade_out=2.0
        )
        
        # 清理临时文件
        if os.path.exists(temp_video):
            os.remove(temp_video)
        
        if not bgm_success:
            print("   ⚠️ BGM添加失败，使用无BGM版本")
            # 如果BGM失败，尝试恢复原视频
            if os.path.exists(temp_video):
                os.rename(temp_video, output_path)
    
    return os.path.exists(output_path) and os.path.getsize(output_path) > 0


# 可用的Manim动画风格
MANIM_STYLES = {
    'write': '手写效果（推荐，最自然）',
    'typewriter': '打字机效果',
    'fade_in': '淡入效果',
    'slide_in': '滑入效果'
}
