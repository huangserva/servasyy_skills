# HUD Element: Combat Effects

## 通用版本

```
Combat Effects:
- Floating damage numbers
- Skill visual effects (particle systems, glowing trails)
- Impact effects (sparks, flashes)
```

## 仙侠MMO版本

```
Combat Effects:
- A large swirling area-of-effect magic circle of bright purple, blue, and white sparkling energy between player and boss, rotating slowly
- Floating damage numbers in orange/red above boss: "-9999", "-12847" (critical hits in larger gold text)
- Sword trail: glowing blue-gold-rainbow arc following player's weapon swing
- Boss attack telegraph: golden light gathering around boss's weapon before strike
- Elemental particles: small glowing orbs (blue, purple, gold) drifting upward from impact points
- Screen-edge vignette effect during intense combat moments
```

### 法阵风格库

| 类型 | 颜色 | 适用场景 |
|------|------|---------|
| 仙道法阵 | 金白 | 治疗、增益、传送 |
| 魔道法阵 | 紫红 | 攻击、诅咒、暗系 |
| 冰系法阵 | 蓝白 | 冰冻、减速 |
| 火系法阵 | 橙红 | 烈焰、范围伤害 |
| 雷系法阵 | 蓝紫 | 雷击、麻痹 |
| 阴阳法阵 | 黑白 | 平衡、封印 |

## 赛博朋克版本

```
Combat Effects:
- Bullet tracers: bright cyan laser-like streaks between player and enemies
- Muzzle flash: bright white-blue burst illuminating nearby rain drops
- Hit sparks: orange-red sparks bursting from impact surfaces
- Explosion: fiery orange explosion with debris particles
- Hacking effect: green data streams flowing from player to target, glitch distortion on enemy
- EMP shockwave: expanding cyan ring distorting air and light
- Blood splatter minimal — replaced by cyber-sparks and data fragments
```

## 使用说明

- 仙侠战斗特效核心是**法阵**+**飘字**+**粒子光效**
- 赛博朋克核心是**弹道**+**火花**+**数据流**
- 伤害数字要浮在空中，有大小差异（暴击大字，普通小字）
- 法阵描述要写明颜色、旋转方向、大小，否则GPT可能画偏
- 粒子效果（飘散的光点/花瓣）是增加画面质感的绝佳细节
