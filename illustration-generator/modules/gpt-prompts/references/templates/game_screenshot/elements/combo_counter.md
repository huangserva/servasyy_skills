# HUD Element: Combo Counter

## 通用版本

```
Bottom Center (above skill bar) — Combo Counter:
- Hit counter showing current combo chain
- Damage bonus percentage
```

## 仙侠MMO版本

```
Bottom Center (above skill bar) — Combo Display:
- Large stylized combo counter: "{{combo_count}}" in fiery orange/gold text
- Below it: "{{combo_bonus}}" in smaller white text
- Visual effect: combo text has flame/energy aura, scales up with higher combos
- Combo milestone effects: at 10/20/50/100 hits, extra visual burst
```

### 常用数值

| 连击数 | 加成描述 | 视觉效果 |
|--------|---------|---------|
| 5连击 | 伤害 +5% | 小字，轻微发光 |
| 10连击 | 伤害 +15% | 中字，橙金色 |
| 23连击 | 伤害 +35% | 大字，火焰光环 |
| 50连击 | 伤害 +80% | 更大字，金紫色爆发 |
| 100连击 | 伤害 +200% | 巨字，全屏闪光 |

## 赛博朋克版本

```
Combat Analytics Overlay (floating near crosshair):
- "CHAIN x{{combo_count}}" in cyan holographic text
- "DMG MULTIPLIER: {{combo_bonus}}" below
- Kill streak counter: "STREAK: {{streak_count}}"
```

## 使用说明

- 仙侠连击计数器用中文数字+火焰效果
- 赛博朋克用英文+全息效果
- 位置通常在技能栏上方或准星附近
- 连击数 + 伤害加成同时显示，增加战斗紧迫感
