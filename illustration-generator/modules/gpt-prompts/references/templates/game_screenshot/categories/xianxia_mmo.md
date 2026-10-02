# Xianxia MMO Game Screenshot Template

仙侠MMO游戏截图模板。基于《齐天大圣·孙悟空》Boss战截图提炼。

## 分类默认值

继承 `base.md`，以下变量有预设值：

| 变量 | 默认值 |
|------|--------|
| `category_label` | xianxia MMORPG |
| `camera_angle` | third-person back view |
| `time_of_day` | ethereal celestial lighting with volumetric golden rays |
| `color_palette` | Warm gold and soft pink/purple palette, pale blue sky |
| `style_instruction` | Ultra HD xianxia MMO game screenshot, Unreal Engine 5 quality rendering, glowing celestial light effects, floating particles and petals |
| `aspect_ratio` | 16:9 |

## 分类特有元素

仙侠MMO区别于其他游戏品类的视觉特征：

### 场景特征（scene_keywords）
- 浮空仙岛、云海、碎裂金色柱子、飞檐楼阁
- 樱花/桃花花瓣飘落、仙气雾霭
- 远景雪山/宫殿/巨佛雕像
- 法阵（金色/紫色/蓝色发光环形阵列）

### 角色特征（character_keywords）
- 汉服/仙侠长裙、飘带、高发髻、发饰步摇
- 发光武器（飞剑、法杖、扇子）
- 技能光效（蓝金紫三色为主）

### Boss特征（boss_keywords）
- 巨大体型（比玩家大3-5倍）
- 华丽铠甲/仙衣、光环、神器
- 名字牌带等级和Buff指示器

### UI风格
- 金色/暖铜色边框，红色血条
- 中文毛笔字体风格
- 粉色/紫色技能图标

## 预设场景模板

### Boss战场景（默认，最常用）

**必填变量：**
- `{{player_description}}` — 玩家外观
- `{{boss_name}}` — Boss名称（中文+英文）
- `{{boss_level}}` — Boss等级
- `{{boss_appearance}}` — Boss外观
- `{{boss_weapon}}` — Boss武器/技能
- `{{scene_description}}` — 场景

**可选变量：**
- `{{player_name}}` — 玩家ID，默认 `剑舞红尘`
- `{{player_level}}` — 玩家等级，默认 `Lv.98`
- `{{player_hp}}` — 玩家血量，默认 `187654/313593 (60%)`
- `{{boss_hp_percent}}` — Boss血量百分比，默认 `85%`
- `{{boss_buff}}` — Boss增益/层数，默认 `x85`
- `{{quest_title}}` — 任务标题
- `{{quest_subtitle}}` — 任务副标题
- `{{combo_count}}` — 连击数，默认 `23连击`
- `{{combo_bonus}}` — 连击加成，默认 `伤害 +35%`
- `{{chat_messages}}` — 聊天消息列表
- `{{skill_names}}` — 技能栏技能名

**完整Prompt模板：**

```
Create an ultra HD xianxia MMORPG game screenshot, third-person back view, epic boss fight.

Subject: {{player_description}}, mid-leap attacking the boss, holding a glowing sword emitting blue-gold-rainbow light.

Boss: {{boss_name}} Lv.{{boss_level}}, {{boss_appearance}}, holding {{boss_weapon}}. Massive glowing golden celestial circular array radiating light behind the boss. Boss is 3x larger than the player.

Scene: {{scene_description}}. Ethereal celestial lighting with volumetric golden rays. Floating pink cherry blossom petals scattered in the air.

Combat Effects: A large swirling area-of-effect magic circle of bright purple, blue, and white sparkling energy between the player and boss.

Composition: Third-person back view, 16:9 widescreen. Player center-left foreground, boss right side, combat effects between them.

Game UI (must be visible, authentic Chinese MMO style):

Top Left — Player Status:
- Circular avatar portrait of player character
- Player name "{{player_name}}" level {{player_level}}
- Red health bar: {{player_hp}}
- "和平" (Peace/PvE mode) indicator
- 6 buff/ability icons in a row, then "变强" (Become Stronger) upgrade button

Top Center — Boss Status:
- Boss title "{{boss_name}} Lv.{{boss_level}}" in ornate gold trim
- Large red boss health bar at {{boss_hp_percent}}, with "{{boss_buff}}" buff indicator at right end

Top Right — Quest Tracker:
- Quest box: "{{quest_title}}"
- Subtitle: "{{quest_subtitle}}" with green progress arrow

Bottom Left — Chat Box:
- Red [系统] system messages about combat events
- Green [世界] world chat player messages cheering
{{chat_messages}}

Bottom Center — Combat & Skill Bar:
- Combat text: "{{combo_count}}" combo counter with "{{combo_bonus}}" bonus below
- Skill hotbar: 4 skills bound to keys 1/2/3/4 (purple/pink glowing icons), 1 larger central ultimate skill, 3 skills on Q/E/R (blue/red/purple icons)
- Function buttons: 目标(Tab), 闪避(Space), F2, 闪现(Blink), 跳跃(Jump)

Bottom Right — Large ultimate/weapon swap icon, purple background

Bottom Left Corner — System: game time, "28ms" ping, "EXP 78.59%" progress

Left Edge — Vertical menu: 战宠(Battle Pet), 宠宝(Pet Treasure) buttons

Style: Ultra HD xianxia MMO game screenshot, Unreal Engine 5 quality rendering. Warm gold and soft pink/purple palette. Glowing celestial light effects, floating particles and petals.

Constraints: All UI text in Chinese characters. UI must look authentic and functional. Boss must be significantly larger than player. No watermark. No photorealistic rendering.
```

### 城镇/集市场景

**额外变量：**
- `{{npc_descriptions}}` — NPC外观列表
- `{{shop_signs}}` — 店铺招牌文字

```
Create an ultra HD xianxia MMORPG game screenshot, third-person back view, town exploration.

Subject: {{player_description}}, standing in the center of a bustling ancient Chinese town square, idle pose.

Scene: Ancient Chinese town with stone-paved square. Wooden architecture with red lanterns, carved window lattices, silk banners. {{npc_descriptions}}. Pink cherry blossom trees in bloom. Far background: layers of palace pavilions with flying eaves and ancient pagodas among misty mountain peaks.

Composition: Third-person back view, 16:9 widescreen. Player center-foreground, town square middle-ground, mountains far background.

Game UI (must be visible, authentic Chinese MMO style):

Top Left — Player Status:
- Circular avatar, player name, level, red health bar (full)

Top Right — Quest Tracker:
- Current quest with progress

Bottom Left — Chat Box:
- [世界] player chat messages, [系统] system announcements

Bottom Center — Skill bar with 8 skill icons and function buttons

Bottom Right Corner — minimap showing town layout

Left Edge — Menu buttons: 背包(Inventory), 任务(Quests), 社交(Social)

Style: Ultra HD xianxia MMO game screenshot, Unreal Engine 5 quality. Warm afternoon sunlight with volumetric light through cherry blossom branches. Warm palette: pink cherry blossoms, golden architecture, jade-green mountains, azure sky.

Constraints: All UI text in Chinese. Town must feel alive with NPCs. No watermark.
```

### 副本/秘境场景

**额外变量：**
- `{{dungeon_name}}` — 副本名
- `{{dungeon_theme}}` — 副本主题（冰雪/火焰/幽暗/...）
- `{{enemy_group}}` — 小怪群描述

```
Create an ultra HD xianxia MMORPG game screenshot, third-person back view, dungeon raid encounter.

Subject: {{player_description}}, fighting group of enemies in a dungeon chamber.

Enemies: {{enemy_group}}.

Scene: {{dungeon_name}} dungeon interior. {{dungeon_theme}} themed environment. Ancient stone chambers with glowing runes, broken pillars, magical barriers. Dim atmospheric lighting with colored accent lights matching the dungeon theme.

Composition: Third-person back view, 16:9 widescreen. Player center, enemies surrounding.

Game UI:
- Player health bar (top left)
- Enemy health bars above each enemy
- Skill bar (bottom center)
- Dungeon progress indicator: "层数 3/10" (Floor 3/10)
- Party member status on left side (4 party members with health bars)
- Combat log messages

Style: Ultra HD xianxia MMO game screenshot, Unreal Engine 5 quality. {{dungeon_theme}} color palette. Dramatic dungeon lighting.

Constraints: All UI in Chinese. Dungeon atmosphere must feel dangerous. No watermark.
```

## Pitfalls

1. **Boss体型必须远大于玩家**：仙侠MMO的Boss通常是3-5倍大小，prompt里要明确写出"3x larger"
2. **法阵是仙侠的标志**：Boss背后一定要有发光法阵/光环，这是仙侠和西方奇幻的最大视觉区别
3. **花瓣和仙气不能少**：飘落的花瓣+体积光是仙侠MMO的氛围核心
4. **HUD要完整但不要过载**：Boss战推荐开全部UI，城镇场景可以只开基础UI
5. **技能栏用中文键位**：1/2/3/4 + Q/E/R 是中国MMO的标准键位
6. **聊天框是氛围利器**：加几条世界频道消息能让截图瞬间"活"起来，但不要太多（3-4条足够）
