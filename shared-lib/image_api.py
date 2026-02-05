#!/usr/bin/env python3
"""
统一图片生成API封装
支持 z-image (本地ComfyUI), volcengine (doubao-4) 和 ApiMart (nano-banana-pro)
基于 prompt_online2 的实现
"""
import os
import yaml
import requests
import time
import base64
from pathlib import Path
from typing import Optional, Tuple


class ImageGenerator:
    """统一的图片生成接口"""

    def __init__(self, provider='auto', config_path=None, custom_priority=None):
        """
        初始化图片生成器

        Args:
            provider: API选择 ('auto', 'google-local', 'modelscope', 'zimage', 'volcengine', 'apimart')
                     auto模式优先级: google-local → modelscope → z-image → volcengine → apimart
            config_path: config.yaml路径，自动搜索多个可能的位置
            custom_priority: 自定义优先级列表，例如: ['modelscope', 'google-local', 'zimage']
                           如果提供，将覆盖默认的auto模式优先级
        """
        self.provider = provider
        self.custom_priority = custom_priority

        # 加载配置文件
        if config_path is None:
            # 优先使用同目录下的 config.yaml
            config_path = Path(__file__).parent / 'config.yaml'

        self.config = self._load_config(config_path)

        # 获取图像模型优先级列表
        self.image_model_priority = self.config.get('defaults', {}).get('image_model_priority', [
            'modelscope', 'google-local', 'zimage', 'volcengine', 'apimart'
        ])
        
        # z-image 配置
        zimage_config = self.config.get('zimage', {})
        self.zimage_base_url = zimage_config.get('base_url', 'http://219.147.109.250:8198/mw/api/v1')
        self.zimage_api_key = zimage_config.get('api_key', '')
        self.zimage_workflow = zimage_config.get('default_workflow', 'z_image_turbo')
        self.zimage_poll_interval = zimage_config.get('poll_interval', 3)
        self.zimage_max_wait = zimage_config.get('max_wait_time', 300)

    def _load_config(self, config_path):
        """加载YAML配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  加载配置文件失败: {e}")
            return {}

    def _build_priority_from_config(self):
        """从配置文件构建优先级列表"""
        # provider名称到(model_name, provider_name)的映射
        provider_mapping = {
            'modelscope': ('z-image-tongyi', 'modelscope'),
            'google-local': ('gemini-3-pro-image', 'google-local'),
            'zimage': ('z-image', 'zimage'),
            'volcengine': ('doubao-4', 'volcengine'),
            'apimart': ('nano-banana-pro', 'apimart')
        }
        
        result = []
        for provider in self.image_model_priority:
            if provider in provider_mapping:
                result.append(provider_mapping[provider])
            else:
                print(f"⚠️  未知的provider: {provider}")
        
        return result

    def generate_newyorker_style(
        self,
        visual_strategy,
        caption='',
        aspect_ratio='16:9',
        max_retries=1
    ):
        """
        生成《纽约客》风格配图

        Args:
            visual_strategy: 视觉描述（英文）
            caption: 底部标题（中文，可选）
            aspect_ratio: 宽高比 ('16:9', '4:3', '1:1')
            max_retries: 最大重试次数

        Returns:
            (image_url, provider): 图片URL和使用的provider
        """
        # 构建完整prompt
        style_prompt = self._build_newyorker_prompt(visual_strategy, caption)

        # 自动选择provider顺序：从配置文件读取优先级
        providers_to_try = []

        if self.provider == 'auto':
            # 如果有自定义优先级，使用自定义顺序
            if self.custom_priority:
                providers_to_try = self._build_custom_priority(self.custom_priority)
                print(f"   🎯 使用自定义优先级: {self.custom_priority}")
            else:
                # 从配置文件读取优先级
                providers_to_try = self._build_priority_from_config()
                print(f"   🎯 使用配置文件优先级: {self.image_model_priority}")
        elif self.provider == 'google-local':
            providers_to_try = [('gemini-3-pro-image', 'google-local')]
        elif self.provider == 'modelscope':
            providers_to_try = [('z-image-tongyi', 'modelscope')]
        elif self.provider == 'zimage':
            providers_to_try = [('z-image', 'zimage')]
        elif self.provider == 'volcengine':
            providers_to_try = [('doubao-4', 'volcengine')]
        elif self.provider == 'apimart':
            providers_to_try = [('nano-banana-pro', 'apimart')]

        # 尝试每个provider
        last_error = None
        for model_name, provider_name in providers_to_try:
            for attempt in range(max_retries):
                try:
                    print(f"   🎨 使用 {model_name} (尝试 {attempt + 1}/{max_retries})...")

                    if provider_name == 'google-local':
                        image_url = self._generate_with_google_local(
                            prompt=style_prompt,
                            model_name=model_name,
                            aspect_ratio=aspect_ratio
                        )
                    elif provider_name == 'modelscope':
                        image_url = self._generate_with_modelscope(
                            prompt=style_prompt,
                            aspect_ratio=aspect_ratio
                        )
                    elif provider_name == 'zimage':
                        image_url = self._generate_with_zimage(
                            prompt=style_prompt,
                            aspect_ratio=aspect_ratio
                        )
                    elif provider_name == 'volcengine':
                        image_url = self._generate_with_volcengine(
                            prompt=style_prompt,
                            model_name=model_name
                        )
                    elif provider_name == 'apimart':
                        image_url = self._generate_with_apimart(
                            prompt=style_prompt,
                            model_name=model_name,
                            aspect_ratio=aspect_ratio
                        )
                    else:
                        raise Exception(f"不支持的provider: {provider_name}")

                    return (image_url, provider_name)

                except Exception as e:
                    last_error = e
                    print(f"   ⚠️  {provider_name} 尝试 {attempt + 1} 失败: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)

            print(f"   ❌ {provider_name} 失败，尝试下一个provider...")

        # 所有provider都失败
        raise Exception(f"所有provider都失败: {last_error}")

    def generate_ukiyoe_style(
        self,
        visual_strategy,
        caption='',
        aspect_ratio='16:9',
        max_retries=1
    ):
        """
        生成日本浮世绘风格配图

        Args:
            visual_strategy: 视觉描述（英文）
            caption: 底部标题（中文，可选）
            aspect_ratio: 宽高比 ('16:9', '4:3', '1:1')
            max_retries: 最大重试次数

        Returns:
            (image_url, provider): 图片URL和使用的provider
        """
        # 构建完整prompt
        style_prompt = self._build_ukiyoe_prompt(visual_strategy, caption)

        # 自动选择provider顺序：从配置文件读取优先级
        providers_to_try = []

        if self.provider == 'auto':
            # 如果有自定义优先级，使用自定义顺序
            if self.custom_priority:
                providers_to_try = self._build_custom_priority(self.custom_priority)
                print(f"   🎯 使用自定义优先级: {self.custom_priority}")
            else:
                # 从配置文件读取优先级
                providers_to_try = self._build_priority_from_config()
                print(f"   🎯 使用配置文件优先级: {self.image_model_priority}")
        elif self.provider == 'google-local':
            providers_to_try = [('gemini-3-pro-image', 'google-local')]
        elif self.provider == 'modelscope':
            providers_to_try = [('z-image-tongyi', 'modelscope')]
        elif self.provider == 'zimage':
            providers_to_try = [('z-image', 'zimage')]
        elif self.provider == 'volcengine':
            providers_to_try = [('doubao-4', 'volcengine')]
        elif self.provider == 'apimart':
            providers_to_try = [('nano-banana-pro', 'apimart')]

        # 尝试每个provider
        last_error = None
        for model_name, provider_name in providers_to_try:
            for attempt in range(max_retries):
                try:
                    print(f"   🎨 使用 {model_name} (尝试 {attempt + 1}/{max_retries})...")

                    if provider_name == 'google-local':
                        image_url = self._generate_with_google_local(
                            prompt=style_prompt,
                            model_name=model_name,
                            aspect_ratio=aspect_ratio
                        )
                    elif provider_name == 'modelscope':
                        image_url = self._generate_with_modelscope(
                            prompt=style_prompt,
                            aspect_ratio=aspect_ratio
                        )
                    elif provider_name == 'zimage':
                        image_url = self._generate_with_zimage(
                            prompt=style_prompt,
                            aspect_ratio=aspect_ratio
                        )
                    elif provider_name == 'volcengine':
                        image_url = self._generate_with_volcengine(
                            prompt=style_prompt,
                            model_name=model_name
                        )
                    elif provider_name == 'apimart':
                        image_url = self._generate_with_apimart(
                            prompt=style_prompt,
                            model_name=model_name,
                            aspect_ratio=aspect_ratio
                        )
                    else:
                        raise Exception(f"不支持的provider: {provider_name}")

                    return (image_url, provider_name)

                except Exception as e:
                    last_error = e
                    print(f"   ⚠️  {provider_name} 尝试 {attempt + 1} 失败: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)

            print(f"   ❌ {provider_name} 失败，尝试下一个provider...")

        # 所有provider都失败
        raise Exception(f"所有provider都失败: {last_error}")

    def generate_raw_style(
        self,
        prompt,
        aspect_ratio='16:9',
        max_retries=1
    ):
        """
        原始模式：直接使用prompt，不添加任何风格描述
        
        Args:
            prompt: 完整提示词（直接传递给模型）
            aspect_ratio: 宽高比 ('16:9', '4:3', '1:1')
            max_retries: 最大重试次数
        
        Returns:
            (image_url, provider): 图片URL和使用的provider
        """
        # 直接使用用户的prompt，不添加风格描述
        
        # 自动选择provider
        providers_to_try = []
        
        if self.provider == 'auto':
            if self.custom_priority:
                providers_to_try = self._build_custom_priority(self.custom_priority)
                print(f"   🎯 使用自定义优先级: {self.custom_priority}")
            else:
                providers_to_try = [
                    ('gemini-3-pro-image', 'google-local'),
                    ('z-image-tongyi', 'modelscope'),
                    ('z-image', 'zimage'),
                    ('doubao-4', 'volcengine'),
                    ('nano-banana-pro', 'apimart')
                ]
        elif self.provider == 'google-local':
            providers_to_try = [('gemini-3-pro-image', 'google-local')]
        elif self.provider == 'modelscope':
            providers_to_try = [('z-image-tongyi', 'modelscope')]
        elif self.provider == 'zimage':
            providers_to_try = [('z-image', 'zimage')]
        elif self.provider == 'volcengine':
            providers_to_try = [('doubao-4', 'volcengine')]
        elif self.provider == 'apimart':
            providers_to_try = [('nano-banana-pro', 'apimart')]
        
        # 尝试每个provider
        last_error = None
        for model_name, provider_name in providers_to_try:
            for attempt in range(max_retries):
                try:
                    print(f"   🎨 使用 {model_name} (尝试 {attempt + 1}/{max_retries})...")
                    
                    if provider_name == 'google-local':
                        image_url = self._generate_with_google_local(
                            prompt=prompt,
                            model_name=model_name,
                            aspect_ratio=aspect_ratio
                        )
                    elif provider_name == 'modelscope':
                        image_url = self._generate_with_modelscope(
                            prompt=prompt,
                            aspect_ratio=aspect_ratio
                        )
                    elif provider_name == 'zimage':
                        image_url = self._generate_with_zimage(
                            prompt=prompt,
                            aspect_ratio=aspect_ratio
                        )
                    elif provider_name == 'volcengine':
                        image_url = self._generate_with_volcengine(
                            prompt=prompt,
                            model_name=model_name
                        )
                    elif provider_name == 'apimart':
                        image_url = self._generate_with_apimart(
                            prompt=prompt,
                            model_name=model_name,
                            aspect_ratio=aspect_ratio
                        )
                    else:
                        raise Exception(f"不支持的provider: {provider_name}")
                    
                    return (image_url, provider_name)
                
                except Exception as e:
                    last_error = e
                    print(f"   ⚠️  {provider_name} 尝试 {attempt + 1} 失败: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
            
            print(f"   ❌ {provider_name} 失败，尝试下一个provider...")
        
        raise Exception(f"所有provider都失败: {last_error}")

    def _build_newyorker_prompt(self, visual_strategy, caption=''):
        """
        构建《纽约客》风格的完整prompt

        注意：
        - 使用中文描述风格特征（避免AI将英文画成文字）
        - visual_strategy是英文场景描述
        - caption是中文底部标题（如果需要）
        """
        # 风格控制（中文描述，避免被画成文字）
        style_description = """
《纽约客》杂志编辑漫画风格：
- 钢笔墨水速写，极简线条艺术
- 黑白素描配朱红色点缀（色号#E34234）
- 干净的白色背景，松弛的线条
- 简洁留白，富有巧思的幽默感
- 图中不要有任何文字、标签、说明
""".strip()

        # 组合完整prompt
        full_prompt = f"{style_description}\n\n场景描述：{visual_strategy}"

        # 如果有caption，添加说明（但不是画在图里）
        if caption:
            full_prompt += f"\n\n底部标题主题：{caption}"

        return full_prompt

    def _build_ukiyoe_prompt(self, visual_strategy, caption=''):
        """
        构建日本浮世绘风格的完整prompt

        注意：
        - 使用中文描述风格特征（避免AI将英文画成文字）
        - visual_strategy是英文场景描述
        - caption是中文底部标题（如果需要）
        """
        # 风格控制（中文描述，避免被画成文字）
        style_description = """
日本浮世绘艺术风格（江户时代木版画）：
- 平面化构图，强烈的装饰性线条
- 鲜艳饱和的色彩：靛蓝、朱红、金黄、翠绿
- 大胆的色块对比，渐变过渡（bokashi技法）
- 简洁的轮廓线，流畅优雅
- 富有诗意的留白，东方美学意境
- 扁平透视，层次分明
- 图中不要有任何文字、标签、印章
""".strip()

        # 组合完整prompt
        full_prompt = f"{style_description}\n\n场景描述：{visual_strategy}"

        # 如果有caption，添加说明（但不是画在图里）
        if caption:
            full_prompt += f"\n\n底部标题主题：{caption}"

        return full_prompt

    def _build_custom_priority(self, priority_list):
        """
        根据用户提供的优先级列表构建providers_to_try
        
        Args:
            priority_list: 优先级列表，例如 ['modelscope', 'google-local', 'volcengine']
            
        Returns:
            providers_to_try 格式的列表
        """
        provider_mapping = {
            'google-local': ('gemini-3-pro-image', 'google-local'),
            'modelscope': ('z-image-tongyi', 'modelscope'),
            'zimage': ('z-image', 'zimage'),
            'volcengine': ('doubao-4', 'volcengine'),
            'apimart': ('nano-banana-pro', 'apimart'),
        }
        
        providers_to_try = []
        for provider_name in priority_list:
            if provider_name in provider_mapping:
                providers_to_try.append(provider_mapping[provider_name])
            else:
                print(f"   ⚠️  未知的provider: {provider_name}，跳过")
        
        return providers_to_try

    def _generate_with_modelscope(self, prompt, aspect_ratio='16:9'):
        """
        使用ModelScope Z-Image Tongyi生成图片
        
        端点: https://api-inference.modelscope.cn/v1/images/generations
        返回: 图片URL
        
        支持的宽高比: 1:1, 4:3, 3:4, 16:9, 9:16
        """
        # 从配置文件读取
        modelscope_config = self.config.get('ModelScope', {})
        base_url = modelscope_config.get('api_base', 'https://api-inference.modelscope.cn/')
        api_key = modelscope_config.get('api_key')
        
        if not api_key:
            raise Exception("ModelScope API key 未配置，请检查 config.yaml")
        
        # 宽高比到尺寸的映射
        size_map = {
            '1:1': '1024x1024',
            '4:3': '1024x768',
            '3:4': '768x1024',
            '16:9': '1792x1024',
            '9:16': '1024x1792',
            '21:9': '2048x896',
        }
        size = size_map.get(aspect_ratio, '1792x1024')  # 默认16:9
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-ModelScope-Async-Mode": "true"
        }
        
        print(f"   📡 请求: {base_url}v1/images/generations")
        print(f"   📝 模型: Tongyi-MAI/Z-Image-Turbo, 尺寸: {size}")
        
        # 提交任务
        import json
        response = requests.post(
            f"{base_url}v1/images/generations",
            headers=headers,
            data=json.dumps({
                "model": "Tongyi-MAI/Z-Image-Turbo",
                "prompt": prompt,
                "size": size
            }, ensure_ascii=False).encode('utf-8')
        )
        
        response.raise_for_status()
        task_id = response.json()["task_id"]
        
        print(f"   ✅ 任务已提交: {task_id}")
        
        # 轮询任务状态
        max_wait = 300  # 最多等5分钟
        start_time = time.time()
        attempt = 0
        
        while True:
            attempt += 1
            elapsed = time.time() - start_time
            
            if elapsed > max_wait:
                raise Exception(f"任务超时 ({max_wait}秒)")
            
            result = requests.get(
                f"{base_url}v1/tasks/{task_id}",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "X-ModelScope-Task-Type": "image_generation"
                }
            )
            result.raise_for_status()
            data = result.json()
            
            status = data.get("task_status", "UNKNOWN")
            print(f"   ⏳ [{attempt}] 状态: {status}, 已用时: {int(elapsed)}秒")
            
            if status == "SUCCEED":
                image_url = data["output_images"][0]
                print(f"   ✅ 生成成功！")
                return image_url
            elif status == "FAILED":
                raise Exception(f"ModelScope任务失败: {data.get('error', 'Unknown error')}")
            
            time.sleep(5)

    def _generate_with_google_local(self, prompt, model_name='gemini-3-pro-image', aspect_ratio='16:9'):
        """
        使用本地Google API生成图片 (http://127.0.0.1:8045/v1)
        
        使用 chat.completions 接口，通过 size 参数指定尺寸
        支持的尺寸: 1024x1024(1:1), 1280x720(16:9), 720x1280(9:16), 1216x896(4:3)
        """
        import base64
        
        # 从配置文件读取
        google_local_config = self.config.get('google-local', {})
        base_url = google_local_config.get('api_base', 'http://127.0.0.1:8045/v1')
        api_key = google_local_config.get('api_key')
        
        if not api_key:
            raise Exception("Google Local API key 未配置，请检查 config.yaml")
        
        # 宽高比到模型后缀的映射
        # 模型命名: gemini-3-pro-image-{aspect} 或 gemini-3-pro-image-2k-{aspect}
        aspect_to_suffix = {
            '1:1': '1x1',
            '4:3': '4x3',
            '3:4': '3x4',
            '16:9': '16x9',
            '9:16': '9x16',
            '21:9': '21x9',
        }
        aspect_suffix = aspect_to_suffix.get(aspect_ratio, '16x9')
        
        # 使用2k分辨率版本以获得更高质量
        actual_model = f"gemini-3-pro-image-2k-{aspect_suffix}"
        
        # 使用 chat.completions 接口
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": actual_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        print(f"   📡 请求: {base_url}/chat/completions")
        print(f"   📝 模型: {actual_model}")
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"Google API错误 {response.status_code}: {response.text}")
        
        result = response.json()
        
        # 从 chat completions 响应中提取图片
        # 响应格式: choices[0].message.content 包含 base64 图片或 URL
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0].get('message', {}).get('content', '')
            
            # 检查是否是 base64 数据
            if content.startswith('![image](data:image'):
                # Markdown格式: ![image](data:image/jpeg;base64,xxxxx)
                # 提取 base64 部分
                import re
                match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', content)
                if match:
                    b64_data = match.group(1)
                else:
                    raise Exception(f"无法解析Markdown图片格式: {content[:100]}...")
            elif content.startswith('data:image'):
                # 格式: data:image/png;base64,xxxxx
                b64_data = content.split(',')[1] if ',' in content else content
            elif content.startswith('/9j/') or content.startswith('iVBOR'):
                # 直接是 base64 数据
                b64_data = content
            else:
                # 可能是 URL 或其他格式
                raise Exception(f"未知的响应格式: {content[:100]}...")
            
            # 保存到临时文件并转换为URL格式
            # 这里我们需要返回一个临时的data URI
            data_uri = f"data:image/jpeg;base64,{b64_data}"
            print(f"   ✅ 获得图片 (base64, ~{len(b64_data)/1024:.0f}KB)")
            return data_uri
        else:
            raise Exception(f"响应中未找到data字段: {result}")

    def _generate_with_zimage(self, prompt, aspect_ratio='16:9'):
        """
        使用 z-image (本地ComfyUI中间件) 生成图片
        
        端点: /generate (提交任务)
        端点: /task/{task_id} (查询状态)
        
        返回: 图片URL
        """
        # 解析宽高比
        width, height = 1024, 1024  # 默认 1:1
        if aspect_ratio == '16:9':
            width, height = 1920, 1080
        elif aspect_ratio == '4:3':
            width, height = 1024, 768
        elif aspect_ratio == '3:4':
            width, height = 768, 1024
        elif aspect_ratio == '2:3':
            width, height = 768, 1152
        
        # 构建请求头
        headers = {'Content-Type': 'application/json'}
        if self.zimage_api_key:
            headers['Authorization'] = f'Bearer {self.zimage_api_key}'
        
        # 提交任务
        payload = {
            'workflow': self.zimage_workflow,
            'params': {
                'prompt': prompt,
                'seed': -1,
                'size': {
                    'width': width,
                    'height': height,
                    'batch_size': 1
                }
            }
        }
        
        print(f"   📡 请求: {self.zimage_base_url}/generate")
        print(f"   📝 工作流: {self.zimage_workflow}, 尺寸: {width}x{height}")
        
        response = requests.post(
            f"{self.zimage_base_url}/generate",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"z-image API错误 {response.status_code}: {response.text}")
        
        data = response.json()
        if data.get('code') != 0:
            raise Exception(f"z-image 提交失败: {data.get('message')}")
        
        task_id = data.get('data', {}).get('task_id')
        if not task_id:
            raise Exception("未获取到任务ID")
        
        print(f"   ✅ 任务已提交: {task_id}")
        
        # 轮询任务状态
        image_url = self._poll_zimage_task(task_id)
        if image_url:
            return image_url
        else:
            raise Exception("z-image 任务失败或超时")
    
    def _poll_zimage_task(self, task_id: str) -> Optional[str]:
        """轮询 z-image 任务状态"""
        start_time = time.time()
        attempt = 0
        
        headers = {'Content-Type': 'application/json'}
        if self.zimage_api_key:
            headers['Authorization'] = f'Bearer {self.zimage_api_key}'
        
        while True:
            attempt += 1
            elapsed = time.time() - start_time
            
            if elapsed > self.zimage_max_wait:
                print(f"   ❌ 任务超时 ({self.zimage_max_wait}秒)")
                return None
            
            try:
                response = requests.get(
                    f"{self.zimage_base_url}/task/{task_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code != 200:
                    print(f"   ⚠️  查询状态失败: {response.status_code}")
                    time.sleep(self.zimage_poll_interval)
                    continue
                
                data = response.json()
                if data.get('code') != 0:
                    time.sleep(self.zimage_poll_interval)
                    continue
                
                task_data = data.get('data', {})
                status = task_data.get('status', 'unknown')
                
                print(f"   ⏳ [{attempt}] 状态: {status}, 已用时: {int(elapsed)}秒")
                
                if status == 'completed':
                    print(f"   ✅ 任务完成!")
                    images = task_data.get('result', {}).get('images', [])
                    if images:
                        return images[0].get('url')
                    return None
                
                elif status == 'failed':
                    print(f"   ❌ 任务失败: {task_data.get('error', 'Unknown')}")
                    return None
                
                elif status == 'cancelled':
                    print(f"   ❌ 任务已取消")
                    return None
                
                elif status in ['pending', 'processing']:
                    time.sleep(self.zimage_poll_interval)
                    continue
                
                else:
                    time.sleep(self.zimage_poll_interval)
                    
            except Exception as e:
                print(f"   ⚠️  轮询出错: {e}")
                time.sleep(self.zimage_poll_interval)

    def _generate_with_volcengine(self, prompt, model_name='doubao-4'):
        """
        使用火山引擎(volcengine) API生成图片

        端点: /images/generations
        文档: https://www.volcengine.com/docs/6791/1298726

        返回: 图片URL
        """
        # 获取配置
        volcengine_config = self.config.get('volcengine', {})
        model_config = self.config.get('image_models', {}).get(model_name, {})

        api_key = volcengine_config.get('api_key')
        base_url = volcengine_config.get('base_url')
        actual_model = model_config.get('model_name', 'doubao-seedream-4-0-250828')
        default_size = model_config.get('default_size', '2K')
        watermark = model_config.get('watermark', True)

        if not api_key or not base_url:
            raise Exception("volcengine配置缺失")

        # 构建请求
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }

        # 火山引擎API格式（参考 ai_client.py:85-91）
        payload = {
            'model': actual_model,
            'prompt': prompt,
            'size': default_size,  # "2K"
            'response_format': 'url',
            'watermark': watermark
        }

        url = f'{base_url.rstrip("/")}/images/generations'

        print(f"   📡 请求: {url}")
        print(f"   📝 模型: {actual_model}, 尺寸: {default_size}")

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            raise Exception(f"volcengine API错误 {response.status_code}: {response.text}")

        result = response.json()

        # 解析返回的图片（参考 ai_client.py:106-107）
        if "data" in result and len(result["data"]) > 0:
            image_url = result["data"][0]["url"]
            print(f"   ✅ 获得图片URL: {image_url[:80]}...")
            return image_url
        else:
            raise Exception(f"响应中未找到图片数据: {result}")

    def _generate_with_apimart(self, prompt, model_name='nano-banana-pro', aspect_ratio='16:9'):
        """
        使用ApiMart API生成图片（异步任务模式）

        端点: /images/generations (提交任务)
        端点: /tasks/{task_id} (查询状态)

        返回: 图片URL
        """
        # 获取配置
        apimart_config = self.config.get('ApiMart', {})
        model_config = self.config.get('image_models', {}).get(model_name, {})

        api_key = apimart_config.get('api_key')
        api_base = apimart_config.get('api_base')
        actual_model = model_config.get('model_name', 'gemini-3-pro-image-preview')

        if not api_key or not api_base:
            raise Exception("ApiMart配置缺失")

        # 步骤1: 提交任务（参考 universal_ai_client.py:640-655）
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }

        payload = {
            'model': actual_model,
            'prompt': prompt,
            'size': aspect_ratio,  # "16:9", "1:1" 等
            'n': 1
        }

        url = f'{api_base.rstrip("/")}/images/generations'

        print(f"   📡 请求: {url}")
        print(f"   📝 模型: {actual_model}, 尺寸: {aspect_ratio}")

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"ApiMart API错误 {response.status_code}: {response.text}")

        result = response.json()
        print(f"   📦 响应: {result}")

        # 步骤2: 检查响应格式（参考 universal_ai_client.py:667-716）
        if 'data' in result and len(result['data']) > 0:
            data_item = result['data'][0]

            # 异步任务模式：获取task_id并轮询
            if 'task_id' in data_item:
                task_id = data_item['task_id']
                print(f"   🔄 收到任务ID: {task_id}，开始轮询...")

                # 轮询任务状态
                image_url = self._poll_apimart_task(api_base, api_key, task_id)

                if image_url:
                    return image_url
                else:
                    raise Exception("任务轮询失败或超时")

            # 同步模式：直接返回URL
            elif 'url' in data_item:
                image_url = data_item['url']
                print(f"   ✅ 获得图片URL: {image_url[:80]}...")
                return image_url
            else:
                raise Exception(f"响应格式异常: {data_item}")
        else:
            raise Exception(f"响应中未找到data字段: {result}")

    def _poll_apimart_task(
        self,
        api_base: str,
        api_key: str,
        task_id: str,
        max_wait_time: int = 300,
        poll_interval: int = 3
    ) -> Optional[str]:
        """
        轮询ApiMart任务状态直到完成

        参考: universal_ai_client.py:418-537

        Args:
            api_base: API base URL
            api_key: API key
            task_id: 任务ID
            max_wait_time: 最大等待时间（秒）
            poll_interval: 轮询间隔（秒）

        Returns:
            图片URL，失败返回None
        """
        start_time = time.time()
        attempt = 0

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        while True:
            attempt += 1
            elapsed = time.time() - start_time

            if elapsed > max_wait_time:
                print(f"   ❌ 任务轮询超时 ({max_wait_time}秒)")
                return None

            try:
                # 查询任务状态
                response = requests.get(
                    f"{api_base.rstrip('/')}/tasks/{task_id}",
                    headers=headers,
                    timeout=10
                )

                if response.status_code != 200:
                    print(f"   ⚠️  查询状态失败: {response.status_code}")
                    return None

                result = response.json()

                if 'data' in result:
                    task_data = result['data']
                    status = task_data.get('status', 'unknown')
                    progress = task_data.get('progress', 0)

                    print(f"   ⏳ [{attempt}] 状态: {status}, 进度: {progress}%, 已用时: {int(elapsed)}秒")

                    # 任务完成
                    if status in ['succeeded', 'completed']:
                        print(f"   ✅ 任务完成!")

                        # 提取图片URL（参考 universal_ai_client.py:484-513）
                        if 'result' in task_data:
                            result_data = task_data['result']

                            # 格式1: result.images[0].url (ApiMart实际格式)
                            if isinstance(result_data, dict) and 'images' in result_data:
                                images = result_data['images']
                                if isinstance(images, list) and len(images) > 0:
                                    first_image = images[0]
                                    if 'url' in first_image:
                                        url_data = first_image['url']
                                        # URL可能是数组或字符串
                                        if isinstance(url_data, list) and len(url_data) > 0:
                                            return url_data[0]
                                        elif isinstance(url_data, str):
                                            return url_data

                            # 格式2: result[0].url
                            elif isinstance(result_data, list) and len(result_data) > 0:
                                first_result = result_data[0]
                                if 'url' in first_result:
                                    return first_result['url']

                        # 其他可能的URL字段
                        if 'url' in task_data:
                            return task_data['url']
                        if 'image_url' in task_data:
                            return task_data['image_url']

                        print(f"   ❌ 任务完成但未找到图片URL: {task_data}")
                        return None

                    # 任务失败
                    elif status in ['failed', 'error']:
                        print(f"   ❌ 任务失败: {task_data.get('error', 'Unknown error')}")
                        return None

                    # 任务进行中
                    elif status in ['pending', 'processing', 'submitted']:
                        time.sleep(poll_interval)
                        continue

                    else:
                        print(f"   ⚠️  未知状态: {status}")
                        time.sleep(poll_interval)
                        continue

                else:
                    print(f"   ❌ 响应中没有data字段: {result}")
                    return None

            except Exception as e:
                print(f"   ⚠️  轮询出错: {e}")
                time.sleep(poll_interval)
                continue

    def save_image(self, image_url, output_path):
        """
        保存图片到本地

        Args:
            image_url: 图片URL（支持http/https或base64）
            output_path: 输出路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 处理base64数据
        if image_url.startswith('data:image'):
            # 格式: data:image/png;base64,iVBORw0KG...
            header, encoded = image_url.split(',', 1)
            image_data = base64.b64decode(encoded)

            with open(output_path, 'wb') as f:
                f.write(image_data)
            print(f"   💾 图片已保存: {output_path}")
            return

        # 处理HTTP URL
        if image_url.startswith('http'):
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"   💾 图片已保存: {output_path}")
            return

        raise ValueError(f"不支持的图片URL格式: {image_url[:100]}...")


def test_api():
    """测试API是否正常工作"""
    generator = ImageGenerator()

    # 简单测试
    test_prompt = "A simple pen and ink sketch of a cat sitting on a book"

    try:
        print("🧪 测试图片生成API...")
        image_url, provider = generator.generate_newyorker_style(
            visual_strategy=test_prompt,
            caption="测试图片",
            aspect_ratio='16:9',
            max_retries=1
        )
        print(f"✅ 测试成功！使用provider: {provider}")
        print(f"   图片URL: {image_url[:100]}...")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


# ============================================================
# 简化接口：供其他脚本直接调用
# ============================================================

def generate_image(
    prompt: str,
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    config_path: Optional[str] = None,
    provider: str = 'auto',
    max_retries: int = 3
) -> bool:
    """
    生成图片的简化接口（通用）

    Args:
        prompt: 完整的生成提示词
        output_path: 输出文件路径
        width: 图片宽度（像素）
        height: 图片高度（像素）
        config_path: 配置文件路径（可选）
        provider: API提供商 ('auto', 'zimage', 'volcengine', 'apimart')
                 auto模式优先级: z-image → doubao-4 → nano-banana-pro
        max_retries: 最大重试次数

    Returns:
        bool: 成功返回True，失败返回False
    """
    try:
        # 如果没有指定配置路径，使用同目录下的 config.yaml
        if config_path is None:
            config_path = str(Path(__file__).parent / 'config.yaml')

        # 创建生成器
        generator = ImageGenerator(provider=provider, config_path=config_path)

        # 确定宽高比
        aspect_ratio = '16:9'  # 默认
        if width == height:
            aspect_ratio = '1:1'
        elif width / height > 1.7:
            aspect_ratio = '16:9'
        elif width / height > 1.2:
            aspect_ratio = '4:3'
        elif width / height < 0.8:
            aspect_ratio = '3:4'

        # 生成图片（使用通用prompt，不强制纽约客风格）
        # 注意：这里我们直接调用底层API，而不是generate_newyorker_style
        providers_to_try = []

        if provider == 'auto':
            # 优先z-image（本地ComfyUI），备选云端API
            providers_to_try = [
                ('z-image', 'zimage'),
                ('doubao-4', 'volcengine'),
                ('nano-banana-pro', 'apimart')
            ]
        elif provider == 'zimage':
            providers_to_try = [('z-image', 'zimage')]
        elif provider == 'volcengine':
            providers_to_try = [('doubao-4', 'volcengine')]
        elif provider == 'apimart':
            providers_to_try = [('nano-banana-pro', 'apimart')]

        # 尝试每个provider
        last_error = None
        for model_name, provider_name in providers_to_try:
            for attempt in range(max_retries):
                try:
                    print(f"   🎨 使用 {model_name} (尝试 {attempt + 1}/{max_retries})...")

                    if provider_name == 'zimage':
                        image_url = generator._generate_with_zimage(
                            prompt=prompt,
                            aspect_ratio=aspect_ratio
                        )
                    elif provider_name == 'volcengine':
                        image_url = generator._generate_with_volcengine(
                            prompt=prompt,
                            model_name=model_name
                        )
                    elif provider_name == 'apimart':
                        image_url = generator._generate_with_apimart(
                            prompt=prompt,
                            model_name=model_name,
                            aspect_ratio=aspect_ratio
                        )
                    else:
                        raise Exception(f"不支持的provider: {provider_name}")

                    # 保存图片
                    generator.save_image(image_url, output_path)
                    return True

                except Exception as e:
                    last_error = e
                    print(f"   ⚠️  {provider_name} 尝试 {attempt + 1} 失败: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)

            print(f"   ❌ {provider_name} 失败，尝试下一个provider...")

        # 所有provider都失败
        print(f"   ❌ 所有provider都失败: {last_error}")
        return False

    except Exception as e:
        print(f"   ❌ generate_image 错误: {e}")
        return False


if __name__ == '__main__':
    # 运行测试
    test_api()
