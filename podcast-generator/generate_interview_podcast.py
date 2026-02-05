#!/usr/bin/env python3
"""
访谈式播客一键生成工具
支持从Markdown文档自动生成双人访谈播客

作者: Droid
版本: 1.0
"""

import subprocess
import os
import sys
import re
from pathlib import Path
import argparse


class InterviewPodcastGenerator:
    """访谈式播客生成器"""
    
    def __init__(self, 
                 female_voice='zh-CN-XiaoyiNeural',
                 male_voice='zh-CN-YunyangNeural',
                 female_rate='+5%',
                 male_rate='+3%',
                 pause_duration=0.3,
                 segment_length=50):
        """
        初始化播客生成器
        
        参数:
            female_voice: 女声ID (默认: 晓伊)
            male_voice: 男声ID (默认: 云扬)
            female_rate: 女声语速 (默认: +5%)
            male_rate: 男声语速 (默认: +3%)
            pause_duration: 对话间停顿时长（秒，默认: 0.3）
            segment_length: 每段对话目标字数（默认: 50）
        """
        self.female_voice = female_voice
        self.male_voice = male_voice
        self.female_rate = female_rate
        self.male_rate = male_rate
        self.pause_duration = pause_duration
        self.segment_length = segment_length
        
        # 检查依赖
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查必要的依赖工具"""
        try:
            subprocess.run(['edge-tts', '--version'], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ edge-tts 未安装")
            print("   安装命令: python3 -m pip install edge-tts --break-system-packages")
            sys.exit(1)
        
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ ffmpeg 未安装")
            print("   macOS安装: brew install ffmpeg")
            sys.exit(1)
    
    def extract_text_from_markdown(self, md_file):
        """从Markdown提取纯文本"""
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 去除Markdown格式
        text = content
        text = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', '', text)  # 图片
        text = re.sub(r'^\*[^\*]+\*$', '', text, flags=re.MULTILINE)  # 图片说明
        text = re.sub(r'^# (.+)$', r'\1', text, flags=re.MULTILINE)  # h1
        text = re.sub(r'^## (.+)$', r'\1', text, flags=re.MULTILINE)  # h2
        text = re.sub(r'^---$', '', text, flags=re.MULTILINE)  # 分隔线
        text = re.sub(r'^> ', '', text, flags=re.MULTILINE)  # 引用
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # 加粗
        
        # 去除emoji
        emoji_pattern = re.compile("["
            u"\U0001F000-\U0001F9FF"
            u"\u2600-\u26FF"
            u"\u2700-\u27BF"
            u"\uFE00-\uFE0F"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        
        # 去除多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def generate_interview_script(self, content, title="访谈播客"):
        """
        将内容转换为访谈式脚本
        
        参数:
            content: 原始文本内容
            title: 播客标题
        
        返回:
            访谈脚本（带晓晓/云扬标记）
        """
        # 提取段落
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # TODO: 使用AI优化成访谈对话（当前版本手动编写）
        # 这里返回基础脚本，实际使用时需要人工或AI改写
        
        script = f"""【访谈式播客】{title}

晓晓：欢迎来到《历史不装》，我是晓晓。
云扬：我是云扬。
晓晓：今天我们来聊一个特别有意思的话题。

"""
        # 将段落转换为对话（简化版，实际需要更智能的处理）
        speaker = '云扬'
        for para in paragraphs[:10]:  # 示例：只处理前10段
            if len(para) > self.segment_length:
                # 分割长段落
                sentences = re.split(r'([。！？])', para)
                current_segment = ''
                for i in range(0, len(sentences), 2):
                    if i + 1 < len(sentences):
                        sentence = sentences[i] + sentences[i+1]
                    else:
                        sentence = sentences[i]
                    
                    if len(current_segment) + len(sentence) <= self.segment_length:
                        current_segment += sentence
                    else:
                        if current_segment:
                            script += f"{speaker}：{current_segment}\n\n"
                            speaker = '晓晓' if speaker == '云扬' else '云扬'
                        current_segment = sentence
                
                if current_segment:
                    script += f"{speaker}：{current_segment}\n\n"
                    speaker = '晓晓' if speaker == '云扬' else '云扬'
            else:
                script += f"{speaker}：{para}\n\n"
                speaker = '晓晓' if speaker == '云扬' else '云扬'
        
        script += """晓晓：今天的内容就到这里。
云扬：感谢收听，我们下期再见。
晓晓：拜拜～
"""
        
        return script
    
    def parse_script(self, script):
        """
        解析访谈脚本
        
        返回: [(speaker, text), ...]
        """
        dialogues = []
        for line in script.split('\n'):
            line = line.strip()
            if line.startswith('晓晓：'):
                dialogues.append(('晓晓', line[3:]))
            elif line.startswith('云扬：'):
                dialogues.append(('云扬', line[3:]))
        return dialogues
    
    def generate_audio_segment(self, speaker, text, output_file):
        """生成单个音频片段"""
        voice = self.female_voice if speaker == '晓晓' else self.male_voice
        rate = self.female_rate if speaker == '晓晓' else self.male_rate
        
        subprocess.run([
            'edge-tts',
            '--voice', voice,
            '--rate', rate,
            '--text', text,
            '--write-media', output_file
        ], capture_output=True, timeout=120, check=True)
    
    def generate_silence(self, duration, output_file):
        """生成静音文件"""
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono',
            '-t', str(duration), '-q:a', '9', '-acodec', 'libmp3lame',
            '-y', output_file
        ], capture_output=True, check=True)
    
    def merge_audio_files(self, file_list, output_file):
        """合并音频文件"""
        list_file = 'temp_filelist.txt'
        with open(list_file, 'w') as f:
            for audio_file in file_list:
                f.write(f"file '{audio_file}'\n")
        
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', list_file,
            '-c', 'copy', '-y', output_file
        ], capture_output=True, check=True)
        
        os.remove(list_file)
    
    def generate_podcast(self, script, output_file, progress_callback=None):
        """
        从脚本生成完整播客
        
        参数:
            script: 访谈脚本文本
            output_file: 输出MP3文件路径
            progress_callback: 进度回调函数 callback(current, total, message)
        """
        dialogues = self.parse_script(script)
        total = len(dialogues)
        
        if total == 0:
            raise ValueError("脚本中没有找到对话内容")
        
        print(f"\n🎙️ 开始生成访谈播客")
        print(f"   对话轮次: {total}")
        print(f"   女声: {self.female_voice} ({self.female_rate})")
        print(f"   男声: {self.male_voice} ({self.male_rate})")
        print(f"   停顿: {self.pause_duration}秒\n")
        
        # 生成音频片段
        audio_segments = []
        temp_files = []
        
        for i, (speaker, text) in enumerate(dialogues, 1):
            if not text:
                continue
            
            segment_file = f'podcast_seg_{i:03d}.mp3'
            temp_files.append(segment_file)
            
            display_text = text[:40] + '...' if len(text) > 40 else text
            print(f"   [{i}/{total}] {speaker}: {display_text}")
            
            try:
                self.generate_audio_segment(speaker, text, segment_file)
                audio_segments.append(segment_file)
                
                if progress_callback:
                    progress_callback(i, total, f"生成 {speaker} 音频")
                    
            except Exception as e:
                print(f"      ❌ 生成失败: {e}")
                continue
        
        if not audio_segments:
            raise ValueError("没有成功生成任何音频片段")
        
        print(f"\n✅ 生成了 {len(audio_segments)} 个音频片段")
        
        # 生成静音
        print(f"⏳ 生成停顿间隔...")
        silence_file = f'silence_{int(self.pause_duration*1000)}ms.mp3'
        self.generate_silence(self.pause_duration, silence_file)
        temp_files.append(silence_file)
        
        # 创建合并列表（音频 + 静音交替）
        merge_list = []
        for i, seg in enumerate(audio_segments):
            merge_list.append(seg)
            if i < len(audio_segments) - 1:
                merge_list.append(silence_file)
        
        # 合并
        print(f"⏳ 合并音频...")
        self.merge_audio_files(merge_list, output_file)
        
        # 清理临时文件
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        # 结果
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / (1024 * 1024)
            print(f"\n✅ 播客生成成功！")
            print(f"   📁 文件: {output_file}")
            print(f"   📊 大小: {size:.2f} MB")
            print(f"   🎤 对话: {len(audio_segments)} 轮")
            print(f"   ⏱️  停顿: {self.pause_duration}秒")
        else:
            raise ValueError("合并失败")


def main():
    parser = argparse.ArgumentParser(
        description='访谈式播客一键生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从脚本文件生成播客
  %(prog)s --script interview.txt --output podcast.mp3
  
  # 从Markdown生成播客（需要先改写为访谈脚本）
  %(prog)s --markdown doc.md --output podcast.mp3
  
  # 自定义参数
  %(prog)s --script interview.txt --output podcast.mp3 \\
           --pause 0.5 --segment-length 50 --female-rate +5%%
        """
    )
    
    parser.add_argument('--script', help='访谈脚本文件（带晓晓/云扬标记）')
    parser.add_argument('--markdown', help='Markdown文档（自动转换为访谈脚本）')
    parser.add_argument('--output', '-o', required=True, help='输出MP3文件')
    parser.add_argument('--pause', type=float, default=0.3, 
                       help='对话间停顿时长（秒，默认0.3）')
    parser.add_argument('--segment-length', type=int, default=50,
                       help='每段对话目标字数（默认50）')
    parser.add_argument('--female-voice', default='zh-CN-XiaoyiNeural',
                       help='女声ID（默认: 晓伊）')
    parser.add_argument('--male-voice', default='zh-CN-YunyangNeural',
                       help='男声ID（默认: 云扬）')
    parser.add_argument('--female-rate', default='+5%',
                       help='女声语速（默认: +5%%）')
    parser.add_argument('--male-rate', default='+3%',
                       help='男声语速（默认: +3%%）')
    
    args = parser.parse_args()
    
    # 检查输入
    if not args.script and not args.markdown:
        parser.error("必须指定 --script 或 --markdown")
    
    # 创建生成器
    generator = InterviewPodcastGenerator(
        female_voice=args.female_voice,
        male_voice=args.male_voice,
        female_rate=args.female_rate,
        male_rate=args.male_rate,
        pause_duration=args.pause,
        segment_length=args.segment_length
    )
    
    # 读取脚本
    if args.script:
        with open(args.script, 'r', encoding='utf-8') as f:
            script = f.read()
    else:
        # 从Markdown生成（简化版）
        text = generator.extract_text_from_markdown(args.markdown)
        script = generator.generate_interview_script(text)
        
        # 保存生成的脚本供用户检查
        script_output = args.output.replace('.mp3', '_script.txt')
        with open(script_output, 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"📝 访谈脚本已生成: {script_output}")
        print(f"   请检查并根据需要修改，然后使用 --script 参数重新生成\n")
    
    # 生成播客
    try:
        generator.generate_podcast(script, args.output)
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
