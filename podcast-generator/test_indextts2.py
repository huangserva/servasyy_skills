#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试IndexTTS2服务"""

from gradio_client import Client

# 连接服务
print("连接IndexTTS2服务...")
client = Client("http://219.147.109.250:7860", httpx_kwargs={"timeout": 300.0})

# 测试参数
text = "欢迎来到历史不装，我是晓晓。"
ref_audio = "workspace/voice_female.wav"
ref_text = "大家好，我是晓晓，很高兴和大家分享。"

print(f"文本: {text}")
print(f"参考音频: {ref_audio}")
print(f"参考文本: {ref_text}")
print("\n开始生成...")

try:
    result = client.predict(
        ref_audio_input=ref_audio,
        ref_text_input=ref_text,
        gen_text_input=text,
        model_choice="F5-TTS",
        remove_silence=False,
        cross_fade_duration_slider=0.15,
        speed_slider=1.0,
        api_name="/basic_tts"
    )
    
    print(f"\n✅ 生成成功！")
    print(f"结果: {result}")
    
except Exception as e:
    print(f"\n❌ 生成失败: {e}")
