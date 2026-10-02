# Game Screenshot Base Template

所有游戏截图模板的通用骨架。分类模板继承此骨架，填充分类特有默认值。

## 变量系统

用 `{{变量名}}` 标记需要填充的变量。分三级：

### 必填变量（每次都要填）
- `{{player_description}}` — 玩家角色外观描述（服装、武器、发型、朝向）
- `{{scene_description}}` — 游戏场景描述（地形、建筑、天空、环境）
- `{{action}}` — 当前正在发生的动作（战斗/施法/跑图/对话/...）

### 常用变量（有分类默认值，可覆盖）
- `{{boss_description}}` — Boss/NPC描述（Boss战时必填）
- `{{camera_angle}}` — 摄像机视角，默认 `third-person back view`
- `{{time_of_day}}` — 时间/光照，默认 `afternoon golden light`
- `{{color_palette}}` — 主色调
- `{{aspect_ratio}}` — 比例，默认 `16:9`

### UI变量（从 elements/ 拼装，按需启用）
- `{{hud_health_bar}}` — 血条
- `{{hud_skill_bar}}` — 技能栏
- `{{hud_minimap}}` — 小地图
- `{{hud_chat_box}}` — 聊天框
- `{{hud_quest_tracker}}` — 任务追踪
- `{{hud_combo_counter}}` — 连击计数
- `{{hud_combat_effects}}` — 战斗特效（伤害数字、法阵、粒子）
- `{{hud_extra}}` — 其他UI元素（道具栏、Buff图标等）

## Prompt 骨架

```
Create an ultra HD {{category_label}} game screenshot, {{camera_angle}}.

Subject: {{player_description}}. {{action}}.

{{#if boss_description}}
Boss: {{boss_description}}.
{{/if}}

Scene: {{scene_description}}. {{time_of_day}}.

Composition: {{camera_angle}}, {{aspect_ratio}} widescreen. Player center-foreground, scene elements at middle-ground and far background.

Game UI (must be visible, game-like quality):
{{hud_health_bar}}
{{hud_skill_bar}}
{{hud_minimap}}
{{hud_chat_box}}
{{hud_quest_tracker}}
{{hud_combo_counter}}
{{hud_combat_effects}}
{{hud_extra}}

Style: {{style_instruction}}. {{color_palette}}.

Constraints: All UI text in Chinese characters. Game UI must look authentic and functional. No watermark. No photorealistic rendering — this is a game screenshot, not a photo.
```

## 设计原则

1. **GPT Image 2 是任务执行模型**：骨架告诉它"这是游戏截图任务"，不是"画一张像游戏的图"
2. **UI是核心卖点**：游戏截图和普通CG的区别就在于HUD。UI元素要明确列出，不能只说"带游戏UI"
3. **变量可组合**：elements/ 下的组件可以任意组合，不用的变量留空即可
4. **分类覆盖默认值**：每个分类模板预设该品类最常见的变量值，减少每次填写量
