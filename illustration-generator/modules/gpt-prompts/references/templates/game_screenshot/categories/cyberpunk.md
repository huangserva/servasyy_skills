# Cyberpunk Game Screenshot Template

赛博朋克风格游戏截图模板。基于 Cyberpunk 2077 / 幻塔都市区 视觉风格。

## 分类默认值

| 变量 | 默认值 |
|------|--------|
| `category_label` | cyberpunk action RPG |
| `camera_angle` | third-person over-the-shoulder view |
| `time_of_day` | neon-lit rainy night, wet reflections on ground |
| `color_palette` | Neon cyan, magenta, and electric blue palette against deep dark shadows |
| `style_instruction` | Cyberpunk 2077 game screenshot quality, neon-lit dystopian city, rain-soaked streets with neon reflections, holographic advertisements |
| `aspect_ratio` | 16:9 |

## 分类特有元素

### 场景特征
- 霓虹灯招牌（中文+英文/日文混合）、全息投影广告
- 雨夜湿地面反射、蒸汽从井盖升起
- 高楼大厦、飞行汽车、全息界面
- 赛博义体改造、机械肢体、LED纹身

### 角色特征
- 机能风/赛博朋克服装（皮夹克、LED配饰、机械义体）
- 发光纹身、全息面罩、义眼
- 武器：智能手枪、螳螂刀、电磁鞭

### UI风格
- 青色/品红色全息UI，半透明
- 像素字体 + 简洁几何线条
- 数据流/黑客面板风格

## 预设场景模板

### 街道枪战场景（默认）

**必填变量：**
- `{{player_description}}` — 玩家外观
- `{{enemy_description}}` — 敌人描述
- `{{scene_description}}` — 街道/区域描述

**完整Prompt模板：**

```
Create an ultra HD cyberpunk action RPG game screenshot, third-person over-the-shoulder view, intense street gunfight.

Subject: {{player_description}}, taking cover behind a crashed car, aiming a smart pistol at enemies ahead. Rain pouring down, neon reflections on wet leather jacket.

Enemies: {{enemy_description}}, spread across the street behind barricades.

Scene: {{scene_description}}. Neon-lit rainy night city street, wet asphalt reflecting cyan and magenta neon signs. Holographic advertisements floating above storefronts. Steam rising from manholes. Flying vehicles passing overhead.

Combat Effects: Bullet tracers in bright cyan streaks, muzzle flash illuminating rain drops, small explosions and sparks from hit surfaces.

Composition: Third-person over-the-shoulder, 16:9 widescreen. Player left-foreground, enemies across the street, deep urban canyon stretching into background.

Game UI (must be visible, cyberpunk holographic style):

Top Left — Player Status:
- Sleek minimalist health bar (cyan glow), shield/armor bar below
- Player level and street cred indicator
- 3 active cyberware buff icons (small holographic icons)

Top Center — Mission:
- Mission objective: "{{mission_objective}}" with waypoint distance
- Sub-objective checklist

Top Right — Mini-map:
- Circular holographic minimap showing street grid, enemy markers (red), objective marker (yellow)

Bottom Left — Hack Panel (collapsed):
- Quick hack menu: 短路(Short Circuit), 义体故障(Malfunction), 吸引(Distract)

Bottom Center — Weapon & Skill Bar:
- Current weapon info: smart pistol icon with ammo count "12/48"
- 4 quick-skill icons (neon-bordered), 1 ultimate skill (pulsing cyan)
- Grenade count, healing item count

Bottom Right — System:
- "威胁等级: 高" (Threat Level: HIGH) warning
- NCPD scanner results on targeted enemy
- Network connection status "28ms"

Style: Cyberpunk 2077 game screenshot quality, neon-lit dystopian city, rain-soaked streets with vivid neon reflections. Deep shadows contrasted by bright cyan and magenta lighting. Holographic UI elements with scan-line effects.

Constraints: All UI text in Chinese + English mix (cyberpunk style). UI must have holographic/translucent feel. Rain must be visible. No watermark. Not a photo — game screenshot rendering.
```

### 驾驶场景

```
Create an ultra HD cyberpunk action RPG game screenshot, cockpit/external chase camera view, high-speed vehicle chase through neon city.

Subject: {{player_description}} driving a cyberpunk sports car at high speed through elevated highway.

Scene: {{scene_description}}. Elevated highway winding between massive skyscrapers covered in holographic billboards. Flying police drones in pursuit. Night city skyline stretching to horizon.

Game UI:
- Speedometer and vehicle health (bottom center)
- GPS route on holographic minimap (top right)
- Police pursuit alert level "★☆☆☆☆" (top center)
- Radio station info, incoming phone call notification
- Rear camera view showing pursuing enemies

Style: Cyberpunk 2077 quality, motion blur on background, sharp focus on car. Neon city lights streaking past.

Constraints: Chinese UI text. Sense of extreme speed. No watermark.
```

## Pitfalls

1. **雨+霓虹是赛博朋克的灵魂**：没有雨的赛博朋克缺乏氛围，默认加雨
2. **全息UI区别于传统HUD**：赛博朋克的UI是半透明、有扫描线效果的，不是仙侠那种金色边框
3. **中英混排是风格**：赛博朋克世界的UI文字自然混合中英文（如"威胁等级: HIGH"）
4. **暗色调+亮高光**：大面积深色阴影，霓虹灯是唯一光源，对比度要极端
5. **街道深度感**：赛博朋克城市要有"深渊"感，高楼从近到远层层叠叠
