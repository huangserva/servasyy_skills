# HUD Element: Skill Bar

## 通用版本

```
Bottom Center — Skill Bar:
- Skill hotbar with 8 skill icons
- Function buttons on the right side
```

## 仙侠MMO版本

```
Bottom Center — Combat & Skill Bar:
- Combat pop-up text: "{{combo_count}}" combo counter with "{{combo_bonus}}" bonus below it
- Skill hotbar, left to right:
  - 4 skills bound to keys 1/2/3/4 (purple/pink glowing icons with Chinese ability names)
  - 1 larger central ultimate skill icon (golden glow, pulsing)
  - 3 skills bound to keys Q/E/R (blue, red, purple icons respectively)
- Function buttons to the right of skill bar:
  - 目标 (Target, Tab), 闪避 (Dodge, Space), F2 (menu), 闪现 (Blink), 跳跃 (Jump)
- Bottom far right: large ultimate/weapon swap icon, purple background with weapon render
```

## 赛博朋克版本

```
Bottom Center — Weapon & Skill Bar:
- Current weapon info: weapon icon with ammo count "12/48"
- 4 quick-skill icons (neon-bordered holographic), 1 ultimate skill (pulsing cyan glow)
- Grenade count indicator, healing item count
- Quick hack shortcut icon
```

## 使用说明

- 仙侠技能栏标准键位：`1/2/3/4` + `Q/E/R`，中央放大招图标
- 赛博朋克偏向武器信息 + 黑客技能的混合栏
- 技能图标要有发光效果，不是扁平静态图标
- 连击计数器 `{{combo_count}}` 格式：`23连击`，配合 `{{combo_bonus}}` 如 `伤害 +35%`
