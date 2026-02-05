#!/usr/bin/env python3
"""
TTS Script Generator
将 Markdown 转换为适合 TTS 朗读的脚本
支持 AI 智能压缩和改写
"""
import re
import json
import argparse
import os
from pathlib import Path
from typing import List, Dict, Optional
# from anthropic import Anthropic


def extract_h2_sections(md_content: str) -> List[Dict]:
    """提取 H2 章节"""
    sections = []
    
    # H1 标题
    h1_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    if h1_match:
        title = h1_match.group(1).strip()
        sections.append({
            'section': 0,
            'title': title,
            'content': title,
            'is_cover': True
        })
    
    # H2 章节
    h2_pattern = r'^##\s+(.+?)$\n\n(.*?)(?=\n##\s|\Z)'
    matches = re.finditer(h2_pattern, md_content, re.MULTILINE | re.DOTALL)
    
    for i, match in enumerate(matches, 1):
        title = match.group(1).strip()
        content = match.group(2).strip()
        
        sections.append({
            'section': i,
            'title': title,
            'content': content,
            'is_cover': False
        })
    
    return sections


def clean_markdown(text: str) -> str:
    """清理 Markdown 格式"""
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def to_spoken_style(text: str) -> str:
    """转换为口语化风格"""
    # 清理格式
    text = clean_markdown(text)
    
    # 口语化处理
    replacements = {
        '。': '。 ',  # 句号后加停顿
        '，': '， ',
        '：': '： ',
        '；': '； ',
        '！': '！ ',
        '？': '？ ',
        '\n\n': ' ',  # 段落间用空格
        '\n': ' ',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def split_by_duration(text: str, target_duration: int = 25, chars_per_second: int = 5) -> List[str]:
    """按目标时长分割文本"""
    target_chars = target_duration * chars_per_second
    
    # 按句号分割
    sentences = text.split('。 ')
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        sentence_length = len(sentence) + 2  # 加上"。 "
        
        if current_length + sentence_length > target_chars and current_chunk:
            # 当前块已满，保存
            chunks.append('。 '.join(current_chunk) + '。')
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    # 保存最后一块
    if current_chunk:
        chunks.append('。 '.join(current_chunk) + '。')
    
    return chunks


def load_visual_config(config_path: Path) -> Optional[Dict]:
    """加载配图配置"""
    if not config_path.exists():
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_tts_script(
    md_file: str,
    with_images: bool = False,
    target_duration: int = 25,
    style: str = 'conversational'
) -> List[Dict]:
    """生成 TTS 脚本"""
    
    md_path = Path(md_file)
    
    # 读取 MD
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 提取章节
    sections = extract_h2_sections(md_content)
    
    # 加载配图配置
    visual_config = None
    if with_images:
        config_path = md_path.parent / 'visual_config.json'
        visual_config = load_visual_config(config_path)
    
    # 生成脚本
    script = []
    
    for section in sections:
        section_num = section['section']
        title = section['title']
        content = section['content']
        is_cover = section['is_cover']
        
        # 转换为口语化
        spoken_text = to_spoken_style(content)
        
        # 封面特殊处理
        if is_cover:
            script.append({
                'section': section_num,
                'title': title,
                'image': 'images/illustrations/cover.png' if with_images else None,
                'tts_text': title,
                'estimated_duration': len(title) / 5.0
            })
            continue
        
        # 按时长分割
        chunks = split_by_duration(spoken_text, target_duration)
        
        # 如果只有一段，直接使用
        if len(chunks) == 1:
            image_path = None
            if with_images and visual_config:
                image_path = f"images/illustrations/illustration_{section_num}.png"
            
            script.append({
                'section': section_num,
                'title': title,
                'image': image_path,
                'tts_text': chunks[0],
                'estimated_duration': len(chunks[0]) / 5.0
            })
        else:
            # 多段，每段一个条目
            for i, chunk in enumerate(chunks):
                image_path = None
                if with_images and visual_config and i == 0:
                    image_path = f"images/illustrations/illustration_{section_num}.png"
                
                script.append({
                    'section': section_num,
                    'title': f"{title} ({i+1}/{len(chunks)})" if len(chunks) > 1 else title,
                    'image': image_path,
                    'tts_text': chunk,
                    'estimated_duration': len(chunk) / 5.0
                })
    
    return script


def main():
    parser = argparse.ArgumentParser(description='TTS Script Generator')
    parser.add_argument('markdown', help='Markdown 文件路径')
    parser.add_argument('--with-images', action='store_true', help='关联配图')
    parser.add_argument('--duration', type=int, default=25, help='每段目标时长（秒）')
    parser.add_argument('--style', default='conversational', help='风格')
    parser.add_argument('-o', '--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    print(f"📝 生成 TTS 脚本: {args.markdown}\n")
    
    script = generate_tts_script(
        args.markdown,
        args.with_images,
        args.duration,
        args.style
    )
    
    # 输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        md_path = Path(args.markdown)
        output_path = md_path.parent / f"{md_path.stem}_tts_script.json"
    
    # 保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    
    # 统计
    total_duration = sum(item['estimated_duration'] for item in script)
    total_chars = sum(len(item['tts_text']) for item in script)
    
    print(f"✅ 生成完成！\n")
    print(f"📊 统计:")
    print(f"   段落数: {len(script)}")
    print(f"   总字数: {total_chars}")
    print(f"   预计时长: {int(total_duration//60)}分{int(total_duration%60)}秒")
    print(f"\n💾 保存到: {output_path}")
    
    # 预览
    print(f"\n📖 预览前3段:\n")
    for item in script[:3]:
        print(f"   [{item['section']}] {item['title']}")
        preview = item['tts_text'][:50].replace('\n', ' ')
        print(f"       {preview}... ({item['estimated_duration']:.1f}秒)")
        if item['image']:
            print(f"       🖼️  {item['image']}")
        print()


if __name__ == '__main__':
    main()
