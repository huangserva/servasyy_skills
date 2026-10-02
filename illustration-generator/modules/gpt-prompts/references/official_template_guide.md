# GPT Image 2 官方推荐提示词模板

来源：OpenAI 官方推荐模板

## 核心理念

老一代图像模型更像"根据关键词抽图"。你写一串风格词，它给你一张视觉上还行的图。

GPT Image 2 更像"视觉任务执行模型"。它更适合接收结构化任务，并且不再拘泥于复杂的提示词结构，可以更多的让AI自主发挥出精美的视觉设计。

## 推荐结构

这张图是什么类型。

最终用途是什么。

谁是主体。

参考图分别负责什么。

要不要文字。

文字出现在哪里。

哪些内容不能动。

哪些内容可以变化。

怎么验收。

## 3.1 从零生成图像

这是最基础的能力。你给文字，它生成一张图。

可用于：海报、封面、广告图、人物图、产品图、信息图、菜单、UI mockup、漫画页、插画、社媒图、幻灯片、教学图。

但这里要注意：从零生成不等于随便描述。

**弱写法：**
```text
画一个高级的咖啡广告，电影感，超清。
```

**强写法：**
```text
Create a vertical coffee campaign poster for social media.

Subject:
A glass of iced coffee on a marble tabletop, with condensation droplets and a small metal spoon.

Scene:
Minimal studio tabletop setup, warm morning light, soft cream background.

Composition:
The drink is centered slightly lower, with space at the top for a headline.

Text:
Render the exact title once: "MORNING BREW".

Style:
Clean premium beverage advertising photo, soft shadows, polished commercial finish.

Constraints:
No watermark, no random extra text, no distorted cup shape.
```

强写法不是因为词更多，而是因为它告诉模型"这是广告图，不是随便画杯咖啡"。

## 3.2 编辑已有图像

你上传一张图，让模型改其中一部分或整体重做风格。

可用于：换衣服、换背景、去掉物体、增加道具、修文字、翻译海报、修改 UI、换产品包装、人物入场景。

**编辑任务最大原则：不是先说要改什么，而是先说什么不能动。**

**弱写法：**
```text
把衣服换成黑色皮衣。
```

**强写法：**
```text
Edit the input image, not a full redraw.

Preserve:
the person's face, identity, hairstyle, body shape, pose, camera angle, background, lighting, shadows, and framing.

Change only:
replace the current jacket with a matte black leather jacket.

Match:
the new jacket must fit the existing pose naturally, with realistic folds, seams, highlights, and contact shadows.

Avoid:
no body reshaping, no face change, no background repaint, no extra accessories.
```

这就是编辑任务的核心：保留项、不变量、目标修改、融合规则。

## 3.3 多参考图合成

多参考图是 GPT Image 2 很重要的生产能力。

你可以给多张图，让它按不同职责读取。比如：
- Image 1 负责画风
- Image 2 负责角色身份
- Image 3 负责服装
- Image 4 负责背景氛围
- Image 5 负责产品外观

但多参考图最大的坑是：模型不知道哪张图说了算。

**弱写法：**
```text
参考这些图，生成一张好看的图。
```

**强写法：**
```text
Reference Roles:
Image 1 is the style master. It controls linework, color palette, shadow style, lighting, and overall finish.
Image 2 is the character identity reference. It controls face identity, hairstyle identity, body proportions, and recognizable aura.
Image 3 is the outfit reference. It controls clothing design, material, and color.
Image 4 is the background mood reference. It controls only environment mood and atmosphere.

Do not mix reference roles.
Do not copy unwanted objects from any reference.
```

多参考图的稳定性，不来自"图多"，而来自"职责清楚"。

## 3.4 文字图和多语言排版

GPT Image 2 的文字能力明显增强，尤其适合做：
- 海报标题
- 菜单
- UI 按钮
- 信息图标签
- 漫画对白
- 图表说明
- 品牌物料
- 多语言排版

但文字能力增强，不代表可以不检查。尤其是中文长句、小字号、密集信息图、菜单价格、表格、医学术语、历史战况、票据、合同类文本，仍然要验收。

**文字图的核心写法：**
```text
Render the exact text once: "高血压是如何形成的".
Place it at the top center in bold, clear Chinese type.
No extra text. No duplicate text. No random English words.
```

如果是复杂拼写，可以逐字母说明：
```text
Spell the word E-C-L-I-P-S-E correctly.
```

如果是菜单，要把栏目和菜名写清楚，不要让模型编。
