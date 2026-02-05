"""
BGM (Background Music) 模块
支持为视频添加背景音乐

功能：
- 添加BGM到视频
- 支持音量调节
- 支持循环播放
- 支持淡入淡出
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, Literal

# BGM 预设目录
BGM_DIR = Path(__file__).parent.parent / 'bgm'

# BGM 风格预设
BGM_STYLES = {
    "upbeat": "轻快欢乐，适合科普、生活类",
    "epic": "史诗震撼，适合历史、纪录片",
    "emotional": "感人温暖，适合人文故事",
    "relaxing": "舒缓平静，适合冥想、自然",
    "corporate": "商务专业，适合科技、商业",
}


def check_ffmpeg() -> bool:
    """检查 FFmpeg 是否安装"""
    return shutil.which("ffmpeg") is not None


def get_video_duration(video_path: str) -> float:
    """获取视频时长（秒）"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"⚠️ 无法获取视频时长: {e}")
        return 0.0


def get_preset_bgm(style: str) -> Optional[str]:
    """获取预设BGM文件路径"""
    if not BGM_DIR.exists():
        return None
    
    # 查找匹配的BGM文件
    for ext in ['mp3', 'wav', 'm4a', 'aac']:
        bgm_file = BGM_DIR / f"{style}.{ext}"
        if bgm_file.exists():
            return str(bgm_file)
    
    # 如果没有匹配的风格，尝试default
    for ext in ['mp3', 'wav', 'm4a', 'aac']:
        bgm_file = BGM_DIR / f"default.{ext}"
        if bgm_file.exists():
            return str(bgm_file)
    
    return None


def list_available_bgm() -> list:
    """列出可用的BGM文件"""
    if not BGM_DIR.exists():
        return []
    
    bgm_files = []
    for ext in ['mp3', 'wav', 'm4a', 'aac']:
        bgm_files.extend(BGM_DIR.glob(f"*.{ext}"))
    
    return [f.stem for f in bgm_files]


def add_bgm_to_video(
    video_path: str,
    bgm_path: str,
    output_path: str,
    bgm_volume: float = 0.3,
    loop: bool = True,
    fade_in: float = 0.0,
    fade_out: float = 2.0,
    normalize: bool = True
) -> bool:
    """
    为视频添加背景音乐
    
    Args:
        video_path: 输入视频路径
        bgm_path: BGM音频路径（或预设风格名如 'upbeat'）
        output_path: 输出视频路径
        bgm_volume: BGM音量 (0.0-1.0)，默认0.3
        loop: 是否循环BGM以匹配视频时长
        fade_in: 淡入时长（秒）
        fade_out: 淡出时长（秒）
        normalize: 是否进行动态音频归一化
    
    Returns:
        bool: 是否成功
    """
    if not check_ffmpeg():
        print("❌ FFmpeg 未安装")
        return False
    
    # 如果bgm_path是预设风格名，获取对应文件
    if not Path(bgm_path).exists():
        preset_bgm = get_preset_bgm(bgm_path)
        if preset_bgm:
            bgm_path = preset_bgm
        else:
            print(f"❌ BGM文件不存在: {bgm_path}")
            return False
    
    # 获取视频时长
    duration = get_video_duration(video_path)
    if duration <= 0:
        print("❌ 无法获取视频时长")
        return False
    
    print(f"🎵 添加BGM: {bgm_path}")
    print(f"   音量: {bgm_volume}, 循环: {loop}, 淡出: {fade_out}s")
    
    # 构建滤镜链
    filter_parts = []
    
    # 原音频：统一格式
    filter_parts.append("[0:a]aresample=44100,aformat=channel_layouts=stereo[orig]")
    
    # BGM：统一格式、调整音量
    bgm_filter = f"[1:a]aresample=44100,aformat=channel_layouts=stereo,volume={bgm_volume}"
    
    # 淡入
    if fade_in > 0:
        bgm_filter += f",afade=t=in:d={fade_in}"
    
    # 淡出
    if fade_out > 0:
        fade_start = max(0, duration - fade_out)
        bgm_filter += f",afade=t=out:st={fade_start}:d={fade_out}"
    
    # 裁剪到视频时长
    bgm_filter += f",atrim=0:{duration}[bgm]"
    filter_parts.append(bgm_filter)
    
    # 混合两路音频
    filter_parts.append("[orig][bgm]amix=inputs=2:duration=first:normalize=0[mixed]")
    
    # 动态归一化（防止过载）
    if normalize:
        filter_parts.append("[mixed]dynaudnorm=p=0.95:m=10[aout]")
        audio_map = "[aout]"
    else:
        audio_map = "[mixed]"
    
    filter_complex = ";".join(filter_parts)
    
    # 构建FFmpeg命令
    cmd = ["ffmpeg", "-y", "-i", video_path]
    
    if loop:
        cmd.extend(["-stream_loop", "-1"])
    
    cmd.extend([
        "-i", bgm_path,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", audio_map,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ BGM添加失败: {result.stderr[:500]}")
            return False
        
        print(f"✅ BGM添加成功: {output_path}")
        return True
    
    except Exception as e:
        print(f"❌ BGM添加异常: {e}")
        return False


def add_bgm_simple(
    video_path: str,
    output_path: str,
    style: Literal["upbeat", "epic", "emotional", "relaxing", "corporate"] = "upbeat",
    volume: float = 0.3
) -> bool:
    """
    简化版：使用预设风格添加BGM
    
    Args:
        video_path: 输入视频路径
        output_path: 输出视频路径
        style: BGM风格
        volume: 音量
    
    Returns:
        bool: 是否成功
    """
    bgm_path = get_preset_bgm(style)
    if not bgm_path:
        print(f"❌ 没有找到预设BGM: {style}")
        print(f"   可用BGM: {list_available_bgm()}")
        return False
    
    return add_bgm_to_video(
        video_path=video_path,
        bgm_path=bgm_path,
        output_path=output_path,
        bgm_volume=volume,
        loop=True,
        fade_out=2.0
    )
