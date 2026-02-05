"""
Podcast Generator Skill
从Markdown文档一键生成访谈式播客
"""

import os
import sys
import subprocess
import re
from pathlib import Path
import json

# 添加共享库路径
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from video.tts import TTSFactory


class PodcastGenerator:
    """播客生成器 - 完整流程自动化"""
    
    def __init__(self, workspace_dir=None, tts_engine='edge-tts', minimax_api_key=None, minimax_group_id=None):
        self.workspace_dir = workspace_dir or os.path.join(os.path.expanduser("~"), ".claude/skills/podcast-generator/workspace")
        os.makedirs(self.workspace_dir, exist_ok=True)

        # TTS引擎选择
        self.tts_engine = tts_engine  # 'edge-tts', 'indextts2', 'minimax'

        # MiniMax配置
        self.minimax_api_key = minimax_api_key or os.getenv('MINIMAX_API_KEY')
        self.minimax_group_id = minimax_group_id or os.getenv('MINIMAX_GROUP_ID')
        self.minimax_female_voice = 'female-tianmei'  # 甜美女声
        self.minimax_male_voice = 'male-qn-qingse'    # 青涩男声

        # 默认参数
        self.female_voice = 'zh-CN-XiaoyiNeural'  # 晓伊
        self.male_voice = 'zh-CN-YunyangNeural'   # 云扬
        self.female_rate = '+5%'
        self.male_rate = '+3%'
        self.pause_duration = 0.1
        self.segment_length = 50
        self.segment_indices: list[int] | None = None  # 只生成指定片段（可选）

        # IndexTTS2服务地址
        self.indextts2_url = "http://219.147.109.250:7860"

        # IndexTTS2参考音频（可自定义）
        self.female_prompt_audio = None  # 女声参考音频路径
        self.male_prompt_audio = None    # 男声参考音频路径
        
        # 多角色声音映射（角色名 -> 参考音频路径）
        self.voice_mapping = {}  # 将在 _prepare_default_prompts 中初始化

        # 如果使用IndexTTS2但没有参考音频，自动生成
        if tts_engine == 'indextts2':
            self._prepare_default_prompts()

        # 初始化 shared-lib TTS 引擎
        self._init_shared_tts_engine()

    def _init_shared_tts_engine(self):
        """初始化 shared-lib TTS 引擎"""
        if self.tts_engine == 'edge-tts':
            self.tts_engine_instance = TTSFactory.create('edge-tts', config={
                'default_voice': self.female_voice,
                'default_rate': self.female_rate
            })
        elif self.tts_engine == 'indextts2':
            # 默认使用 shared-lib/voices 目录下的参考音频
            voices_dir = Path.home() / '.claude' / 'skills' / 'shared-lib' / 'voices'
            default_female_prompt = voices_dir / 'female.wav'
            default_male_prompt = voices_dir / 'male.wav'

            self.tts_engine_instance = TTSFactory.create('indextts2', config={
                'url': self.indextts2_url,
                'female_prompt': str(self.female_prompt_audio or default_female_prompt),
                'male_prompt': str(self.male_prompt_audio or default_male_prompt)
            })
        elif self.tts_engine == 'minimax':
            self.tts_engine_instance = TTSFactory.create('minimax', config={
                'api_key': self.minimax_api_key,
                'group_id': self.minimax_group_id
            })
        elif self.tts_engine == 'cosyvoice3':
            self.tts_engine_instance = TTSFactory.create('cosyvoice3', config={
                'cosyvoice_dir': os.path.expanduser('~/CosyVoice'),
            })
            # CosyVoice3 也需要准备声音映射
            if not self.voice_mapping:
                self._prepare_default_prompts()
        else:
            raise ValueError(f"不支持的 TTS 引擎: {self.tts_engine}")
    
    def _prepare_default_prompts(self):
        """准备参考音频（优先使用 shared-lib/voices）"""
        # 优先使用 shared-lib/voices 目录下的参考音频
        voices_dir = Path.home() / '.claude' / 'skills' / 'shared-lib' / 'voices'
        shared_female = voices_dir / 'female.wav'
        shared_male = voices_dir / 'male.wav'
        
        # workspace 下的备用音频
        workspace_female = os.path.join(self.workspace_dir, 'voice_female.wav')
        workspace_male = os.path.join(self.workspace_dir, 'voice_male.wav')
        
        # 初始化4声音映射
        self.voice_mapping = {}
        
        # 共享女声 -> 小丽
        if shared_female.exists():
            self.female_prompt_audio = str(shared_female)
            self.voice_mapping['小丽'] = str(shared_female)
            print(f"   🎤 小丽 -> shared-lib/voices/female.wav")
        
        # 共享男声 -> 大伟
        if shared_male.exists():
            self.male_prompt_audio = str(shared_male)
            self.voice_mapping['大伟'] = str(shared_male)
            print(f"   🎤 大伟 -> shared-lib/voices/male.wav")

        # 共享讲解女声 -> 讲解员
        shared_lecture = voices_dir / 'female_lecture.wav'
        if shared_lecture.exists():
            self.voice_mapping['讲解员'] = str(shared_lecture)
            print(f"   🎤 讲解员 -> shared-lib/voices/female_lecture.wav")
        
        # workspace女声 -> 美美
        if os.path.exists(workspace_female):
            self.voice_mapping['美美'] = workspace_female
            print(f"   🎤 美美 -> workspace/voice_female.wav")
        
        # workspace男声 -> 阿刚
        if os.path.exists(workspace_male):
            self.voice_mapping['阿刚'] = workspace_male
            print(f"   🎤 阿刚 -> workspace/voice_male.wav")
        
        # 兼容旧格式：晓晓/云扬
        if self.female_prompt_audio:
            self.voice_mapping['晓晓'] = self.female_prompt_audio
        if self.male_prompt_audio:
            self.voice_mapping['云扬'] = self.male_prompt_audio
        
        # 如果共享录音都存在，直接返回
        if self.female_prompt_audio and self.male_prompt_audio:
            return
        
        print("🎵 准备默认音色参考音频...")
        
        # 生成女声样本
        if not os.path.exists(female_prompt):
            sample_text = "大家好，我是晓晓，欢迎来到播客节目。"
            try:
                subprocess.run([
                    'edge-tts',
                    '--voice', self.female_voice,
                    '--rate', self.female_rate,
                    '--text', sample_text,
                    '--write-media', female_prompt
                ], capture_output=True, timeout=30, check=True)
                self.female_prompt_audio = female_prompt
                print(f"   ✅ 女声样本已生成")
            except Exception as e:
                print(f"   ⚠️  女声样本生成失败: {e}")
        
        # 生成男声样本
        if not os.path.exists(male_prompt):
            sample_text = "大家好，我是云扬，很高兴和大家分享。"
            try:
                subprocess.run([
                    'edge-tts',
                    '--voice', self.male_voice,
                    '--rate', self.male_rate,
                    '--text', sample_text,
                    '--write-media', male_prompt
                ], capture_output=True, timeout=30, check=True)
                self.male_prompt_audio = male_prompt
                print(f"   ✅ 男声样本已生成\n")
            except Exception as e:
                print(f"   ⚠️  男声样本生成失败: {e}\n")
    
    def extract_text_from_markdown(self, md_file):
        """步骤1: 从Markdown提取纯文本"""
        print("📖 步骤1: 提取纯文本...")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 去除Markdown格式
        text = content
        text = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', '', text)  # 图片
        text = re.sub(r'^\*[^\*]+\*$', '', text, flags=re.MULTILINE)  # 图片说明
        text = re.sub(r'^# (.+)$', r'\1', text, flags=re.MULTILINE)  # h1
        text = re.sub(r'^## (.+)$', r'\1', text, flags=re.MULTILINE)  # h2
        text = re.sub(r'^### (.+)$', r'\1', text, flags=re.MULTILINE)  # h3
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
        
        print(f"   ✅ 提取完成，字数: {len(text)}\n")
        return text.strip()
    
    def generate_interview_script_ai(self, content, title="播客"):
        """步骤2: 检测是否已是脚本格式，或提示用户生成"""
        # 检测是否已经是脚本格式（支持两种格式）
        # 格式1: 角色|情感|文本 (servasyy格式)
        # 格式2: 角色[情感]：文本 或 角色：文本
        import re
        # 支持多角色格式检测：晓晓、云扬、小丽、大伟、美美、阿刚等
        script_pattern = r'(晓晓|云扬|小丽|大伟|美美|阿刚)\|'
        if re.search(script_pattern, content) or \
           re.search(r'晓晓[\[：:]', content) or re.search(r'云扬[\[：:]', content):
            print("🤖 步骤2: 检测到已是脚本格式，直接使用\n")
            return content
        
        print("🤖 步骤2: 需要生成访谈脚本")
        print("   ⚠️  请先让Claude根据文章生成真实的访谈对话脚本")
        print("   💡 Claude会深度理解内容，生成口语化、角色清晰的对话\n")
        print("   然后使用生成的脚本文件重新运行：")
        print("   python skill.py /tmp/article.md --script 脚本.txt --output 播客.mp3\n")
        return None
    
    def parse_script(self, script):
        """步骤3: 解析脚本（支持两种情感标记格式）"""
        print("📝 步骤3: 解析脚本...")
        
        # 支持的情感词列表（不做转换，保留原始情感词，让各 TTS 引擎自己处理）
        supported_emotions = {
            'cheerful', 'angry', 'sad', 'fearful', 'excited', 'nervous',
            'confused', 'disgruntled', 'serious', 'calm', 'gentle', 'chat',
            '开心', '生气', '悲伤', '恐惧', '低落', '惊喜', '平静',
        }
        
        dialogues = []
        for line in script.split('\n'):
            line = line.strip()
            if not line or line.startswith('【'):  # 跳过空行和章节标题
                continue
            
            emotion = None
            speaker = None
            text = None
            
            # 格式1: 角色|情感|文本 (servasyy格式)
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    speaker = parts[0].strip()
                    emotion_tag = parts[1].strip()
                    text = '|'.join(parts[2:]).strip()  # 文本中可能有|
                    # 保留原始情感词，不做转换
                    if emotion_tag in supported_emotions:
                        emotion = emotion_tag
            # 格式2: 角色[情感]：文本 或 角色：文本
            elif line.startswith('晓晓') or line.startswith('云扬'):
                if line.startswith('晓晓'):
                    speaker = '晓晓'
                    rest = line[2:]
                else:
                    speaker = '云扬'
                    rest = line[2:]
                
                # 检查情感标记 [xxx]
                if rest.startswith('['):
                    end = rest.find(']')
                    if end > 0:
                        emotion_tag = rest[1:end]
                        # 保留原始情感词，不做转换
                        if emotion_tag in supported_emotions:
                            emotion = emotion_tag
                        rest = rest[end+1:]
                
                # 去掉冒号
                if rest.startswith('：') or rest.startswith(':'):
                    rest = rest[1:]
                text = rest.strip()
            
            if speaker and text:
                dialogues.append((speaker, text, emotion))
        
        print(f"   ✅ 解析完成，共{len(dialogues)}轮对话\n")
        return dialogues
    
    def generate_audio_segments(self, dialogues):
        """步骤4: 生成音频片段（使用 shared-lib TTS）"""
        print(f"🎤 步骤4: 生成{len(dialogues)}个音频片段（{self.tts_engine}）...\n")

        # 清理旧的音频片段文件，避免与其他项目混淆
        if self.segment_indices is None:
            # 只有在生成全部片段时才清理（避免部分重新生成时误删）
            workspace_path = Path(self.workspace_dir)
            old_segments = list(workspace_path.glob('seg_*.wav')) + list(workspace_path.glob('seg_*.mp3'))
            if old_segments:
                print(f"   🧹 清理旧音频片段: {len(old_segments)} 个文件")
                for f in old_segments:
                    f.unlink()

        audio_files = []
        temp_files = []

        for i, item in enumerate(dialogues, 1):
            # 支持新格式 (speaker, text, emotion) 和旧格式 (speaker, text)
            if len(item) == 3:
                speaker, text, emotion = item
            else:
                speaker, text = item
                emotion = None

            if not text:
                continue

            # 选择声音
            if self.tts_engine == 'indextts2' or self.tts_engine == 'cosyvoice3':
                # IndexTTS2 和 CosyVoice3 输出 wav 格式
                output_file = os.path.join(self.workspace_dir, f'seg_{i:03d}.wav')
                # 使用 voice_mapping 查找角色对应的参考音频
                if speaker in self.voice_mapping:
                    voice = self.voice_mapping[speaker]
                else:
                    # 回退到默认：女声角色用 female，其他用 male
                    voice = self.female_prompt_audio if speaker in ['晓晓', '小丽', '美美'] else self.male_prompt_audio
            else:
                # Edge TTS 和 MiniMax 输出 mp3 格式
                output_file = os.path.join(self.workspace_dir, f'seg_{i:03d}.mp3')

                if self.tts_engine == 'minimax':
                    # MiniMax 使用自己的 voice_id
                    voice = self.minimax_female_voice if speaker == '晓晓' else self.minimax_male_voice
                else:
                    # Edge TTS 使用 voice ID
                    voice = self.female_voice if speaker == '晓晓' else self.male_voice

            # 如果指定了 segment_indices，跳过不在列表中的片段
            # （保留已存在的旧文件用于合并，不加入 temp_files 清理列表）
            if self.segment_indices is not None and i not in self.segment_indices:
                if os.path.exists(output_file):
                    print(f"   [{i}/{len(dialogues)}] ⏭️ 跳过（使用已存在的文件）")
                    audio_files.append(output_file)
                    # 注意：不加入 temp_files，避免被清理
                else:
                    print(f"   [{i}/{len(dialogues)}] ⚠️ 跳过（文件不存在）")
                continue

            display_text = text[:35] + '...' if len(text) > 35 else text
            emo_tag = f"[{list(emotion.keys())[0] if isinstance(emotion, dict) else emotion}]" if emotion else ""
            print(f"   [{i}/{len(dialogues)}] {speaker}{emo_tag}: {display_text}")

            # 构建参数
            kwargs = {}

            # Edge TTS 特定参数
            if self.tts_engine == 'edge-tts':
                kwargs['rate'] = self.female_rate if speaker == '晓晓' else self.male_rate
                # Edge TTS 不支持情感，忽略 emotion

            # IndexTTS2 特定参数
            elif self.tts_engine == 'indextts2':
                if emotion:
                    # IndexTTS2 情感映射（原始情感词 -> 向量格式）
                    indextts2_emotion_map = {
                        'cheerful': {'vec1': 0.3},
                        'angry': {'vec2': 0.3},
                        'sad': {'vec3': 1.0},
                        'fearful': {'vec4': 1.0},
                        'excited': {'vec1': 0.5, 'vec7': 0.5},
                        'nervous': {'vec4': 0.4},
                        'confused': {'vec6': 0.3},
                        'disgruntled': {'vec5': 0.6},
                        'serious': {'vec8': 0.7},
                        'calm': None,
                        'gentle': {'vec8': 0.8, 'vec1': 0.3},
                        'chat': None,
                        '开心': {'vec1': 1.0},
                        '生气': {'vec2': 1.0},
                        '悲伤': {'vec3': 1.0},
                        '恐惧': {'vec4': 1.0},
                        '低落': {'vec6': 1.0},
                        '惊喜': {'vec7': 1.0},
                        '平静': {'vec8': 1.0},
                    }
                    mapped_emotion = indextts2_emotion_map.get(emotion)
                    if mapped_emotion:
                        kwargs['emotion'] = mapped_emotion
                kwargs['emo_weight'] = 0.7 if speaker == '晓晓' else 0.6
                kwargs['temperature'] = 0.85 if speaker == '晓晓' else 0.75

            # MiniMax 特定参数
            elif self.tts_engine == 'minimax':
                if emotion:
                    # MiniMax 使用简单的情感映射
                    emotion_map = {
                        'cheerful': 'happy',
                        'chat': 'neutral',
                        'calm': 'neutral',
                        'serious': 'serious',
                        'gentle': 'gentle',
                        'fearful': 'fearful',
                        'sad': 'sad',
                        'angry': 'angry',
                        'disgruntled': 'angry'
                    }
                    kwargs['emotion'] = emotion_map.get(emotion, 'neutral') if isinstance(emotion, str) else 'neutral'

            # CosyVoice3 特定参数
            elif self.tts_engine == 'cosyvoice3':
                # 直接传递原始情感词，cosyvoice3.py 内部会映射到英文指令
                if emotion:
                    kwargs['emotion'] = emotion

            # 重试3次
            success = False
            for attempt in range(3):
                try:
                    result = self.tts_engine_instance.generate(
                        text=text,
                        voice=voice,
                        output_path=output_file,
                        **kwargs
                    )

                    if result and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                        audio_files.append(output_file)
                        temp_files.append(output_file)
                        success = True
                        break

                except Exception as e:
                    if attempt < 2:
                        import time
                        time.sleep(1)
                        continue
                else:
                    print(f"      ❌ 生成失败(重试3次): {e}")

            if not success:
                print(f"      ⚠️  跳过此段，继续生成...")

        print(f"\n   ✅ 音频生成完成（实际生成: {len(audio_files)}/{len(dialogues)} 片段）\n")
        return audio_files, temp_files

    def generate_silence(self):
        """步骤5: 生成静音"""
        print(f"🔇 步骤5: 生成停顿间隔({self.pause_duration}秒)...")
        
        silence_file = os.path.join(self.workspace_dir, 'silence.mp3')
        
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono',
            '-t', str(self.pause_duration), '-q:a', '9', 
            '-acodec', 'libmp3lame', '-y', silence_file
        ], capture_output=True, check=True)
        
        print(f"   ✅ 静音生成完成\n")
        return silence_file
    
    def merge_audio(self, audio_files, dialogues, output_file):
        """步骤6: 合并音频（智能停顿）"""
        print("🎬 步骤6: 合并音频（智能停顿）...")
        
        # 生成两种停顿（使用22050Hz采样率匹配IndexTTS2输出）
        short_pause = os.path.join(self.workspace_dir, 'pause_short.wav')
        long_pause = os.path.join(self.workspace_dir, 'pause_long.wav')
        
        # 短停顿0.3秒（同一人连续说话）
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=22050:cl=mono',
            '-t', '0.3', '-acodec', 'pcm_s16le', '-y', short_pause
        ], capture_output=True, check=True)
        
        # 长停顿1秒（换人说话）
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=22050:cl=mono',
            '-t', '1.0', '-acodec', 'pcm_s16le', '-y', long_pause
        ], capture_output=True, check=True)
        
        # 创建文件列表，根据说话人切换选择停顿
        # 收集所有存在的片段文件（不管是否刚生成）
        import re
        from pathlib import Path
        filelist = os.path.join(self.workspace_dir, 'filelist.txt')
        
        # 找出所有音频文件（wav 或 mp3），按数字排序
        workspace_path = Path(self.workspace_dir)
        # 优先查找 wav 文件（IndexTTS2），如果找不到则查找 mp3（Edge TTS/MiniMax）
        all_segments = sorted(workspace_path.glob('seg_*.wav'), key=lambda f: int(f.stem.split('_')[1]))
        if not all_segments:
            all_segments = sorted(workspace_path.glob('seg_*.mp3'), key=lambda f: int(f.stem.split('_')[1]))
        
        with open(filelist, 'w') as f:
            for i, audio in enumerate(all_segments):
                f.write(f"file '{audio}'\n")
                if i < len(all_segments) - 1:
                    # 从文件名提取索引（支持 wav 和 mp3）
                    current_match = re.search(r'seg_(\d+)\.(wav|mp3)', str(audio))
                    next_audio = all_segments[i + 1]
                    next_match = re.search(r'seg_(\d+)\.(wav|mp3)', str(next_audio))
                    
                    if current_match is None or next_match is None:
                        continue
                    
                    current_idx = int(current_match.group(1))
                    next_idx = int(next_match.group(1))
                    
                    current_speaker = dialogues[current_idx - 1][0] if current_idx - 1 < len(dialogues) else None
                    next_speaker = dialogues[next_idx - 1][0] if next_idx - 1 < len(dialogues) else None
                    
                    if current_speaker == next_speaker:
                        # 同一人，短停顿
                        f.write(f"file '{short_pause}'\n")
                    else:
                        # 换人，长停顿
                        f.write(f"file '{long_pause}'\n")
        
        # 合并（重新编码以支持wav转mp3）
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', filelist, '-acodec', 'libmp3lame', '-q:a', '2', '-y', output_file
        ], capture_output=True, check=True)
        
        print(f"   ✅ 合并完成（同人0.3秒，换人1秒）\n")
    
    def cleanup(self, temp_files):
        """清理临时文件"""
        print("🧹 清理临时文件...")
        
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
        
        # 清理其他临时文件（不删除已生成的 seg_*，保留用于重新合并）
        # 清理旧的格式文件（如果当前使用 IndexTTS2/CosyVoice3，则清理 mp3；如果使用其他引擎，则清理 wav）
        if self.tts_engine == 'indextts2' or self.tts_engine == 'cosyvoice3':
            cleanup_patterns = ['seg_*.mp3', 'pause_short.mp3', 'pause_long.mp3', 'silence.mp3', 'filelist.txt']
        else:
            cleanup_patterns = ['seg_*.wav', 'pause_short.wav', 'pause_long.wav', 'silence.mp3', 'filelist.txt']

        for pattern in cleanup_patterns:
            for f in Path(self.workspace_dir).glob(pattern):
                if f.exists():
                    f.unlink()
        
        print("   ✅ 清理完成\n")
    
    def generate_podcast(self, md_file, output_file, title=None):
        """完整流程：从Markdown生成播客"""
        print("=" * 60)
        print("🎙️  访谈式播客生成器 - 完整流程")
        print("=" * 60)
        print()
        
        # 自动生成标题
        if not title:
            title = Path(md_file).stem
        
        print(f"📁 输入: {md_file}")
        print(f"📁 输出: {output_file}")
        print(f"📝 标题: {title}")
        print(f"🎤 女声: {self.female_voice} ({self.female_rate})")
        print(f"🎤 男声: {self.male_voice} ({self.male_rate})")
        print(f"⏸️  停顿: {self.pause_duration}秒")
        print()
        print("=" * 60)
        print()
        
        try:
            # 步骤1: 提取文本
            content = self.extract_text_from_markdown(md_file)
            
            # 保存纯文本
            text_file = os.path.join(self.workspace_dir, f"{title}_纯文本.txt")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 步骤2: 生成访谈脚本
            script = self.generate_interview_script_ai(content, title)
            
            # 如果没有脚本，提示用户并退出
            if script is None:
                print("⚠️  请先让Claude生成访谈脚本，然后使用 --script 参数重新运行")
                return None
            
            # 保存脚本
            script_file = os.path.join(self.workspace_dir, f"{title}_访谈脚本.txt")
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)
            print(f"💾 脚本已保存: {script_file}")
            print("   （可以手动编辑此脚本后重新生成播客)\n")
            
            # 步骤3: 解析脚本
            dialogues = self.parse_script(script)
            
            # 解析片段索引（如果有）
            segment_indices = None
            if hasattr(self, 'segment_indices') and self.segment_indices:
                print(f"   🎯 只生成指定片段: {self.segment_indices}\n")
            
            # 步骤4: 生成音频片段
            audio_files, temp_files = self.generate_audio_segments(dialogues)
            
            if not audio_files:
                raise ValueError("没有成功生成任何音频片段")
            
            # 步骤5: 生成静音
            silence_file = self.generate_silence()
            temp_files.append(silence_file)
            
            # 步骤6: 合并音频（智能停顿）
            self.merge_audio(audio_files, dialogues, output_file)
            
            # 清理临时文件
            self.cleanup(temp_files)
            
            # 结果
            if os.path.exists(output_file):
                size = os.path.getsize(output_file) / (1024 * 1024)
                
                print("=" * 60)
                print("✅ 播客生成成功！")
                print("=" * 60)
                print()
                print(f"📁 文件: {output_file}")
                print(f"📊 大小: {size:.2f} MB")
                print(f"🎤 对话: {len(dialogues)} 轮")
                print(f"⏱️  停顿: {self.pause_duration}秒")
                print()
                print("🎧 可以直接播放了！")
                print()
                
                return output_file
            else:
                raise ValueError("最终文件生成失败")
                
        except Exception as e:
            print(f"\n❌ 生成失败: {e}")
            return None


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='访谈式播客生成器 - 从Markdown一键生成播客')
    parser.add_argument('markdown', help='Markdown文件路径')
    parser.add_argument('--output', '-o', help='输出MP3文件路径（默认：与输入同名）')
    parser.add_argument('--title', help='播客标题（默认：文件名）')
    parser.add_argument('--female-voice', default='zh-CN-XiaoyiNeural', 
                       help='女声ID（默认：晓伊）')
    parser.add_argument('--male-voice', default='zh-CN-YunyangNeural',
                       help='男声ID（默认：云扬）')
    parser.add_argument('--pause', type=float, default=0.1,
                       help='对话间停顿（秒，默认：0.1）')
    parser.add_argument('--tts-engine', default='edge-tts', choices=['edge-tts', 'indextts2', 'minimax', 'cosyvoice3'],
                       help='TTS引擎（默认：edge-tts）')
    parser.add_argument('--female-prompt', help='IndexTTS2女声参考音频路径')
    parser.add_argument('--male-prompt', help='IndexTTS2男声参考音频路径')
    parser.add_argument('--minimax-api-key', help='MiniMax API Key')
    parser.add_argument('--minimax-group-id', help='MiniMax Group ID')
    parser.add_argument('--segments', help='只生成指定片段（逗号分隔，如：18,20,24,28,46,48,50）')

    args = parser.parse_args()
    
    # 生成输出文件名
    if not args.output:
        md_path = Path(args.markdown)
        args.output = md_path.parent / f"{md_path.stem}_播客.mp3"
    
    # 创建生成器
    generator = PodcastGenerator(
        tts_engine=args.tts_engine,
        minimax_api_key=args.minimax_api_key,
        minimax_group_id=args.minimax_group_id
    )
    generator.female_voice = args.female_voice
    generator.male_voice = args.male_voice
    generator.pause_duration = args.pause
    
    # 设置IndexTTS2参考音频
    if args.female_prompt:
        generator.female_prompt_audio = args.female_prompt
    if args.male_prompt:
        generator.male_prompt_audio = args.male_prompt
    
    # 设置只生成指定片段
    if args.segments:
        try:
            generator.segment_indices = [int(x.strip()) for x in args.segments.split(',')]
            print(f"🎯 只生成指定片段: {generator.segment_indices}\n")
        except ValueError:
            print(f"❌ 无效的片段编号格式: {args.segments}")
            sys.exit(1)
    
    # 生成播客
    result = generator.generate_podcast(
        args.markdown,
        str(args.output),
        args.title
    )
    
    sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()
