# HUD Element: Health Bar

## 通用版本（大部分游戏适用）

```
Top Left — Player Status:
- Circular avatar portrait of player character
- Player name and level
- Red health bar with current/max values
```

## 仙侠MMO版本

```
Top Left — Player Status:
- Circular avatar portrait (Chinese ink painting style)
- Player name "{{player_name}}" level {{player_level}} in gold text
- Red health bar with ornate gold border: {{player_hp}}
- "{{mode}}" (PvE/PvP mode) indicator below health bar
- 6 buff/ability icons in a row with gold frames
- "变强" (Become Stronger) upgrade button with upward arrow icon
```

## 赛博朋克版本

```
Top Left — Player Status:
- Sleek minimalist health bar (cyan holographic glow)
- Shield/armor bar below health bar
- Player level and street cred indicator
- 3 active cyberware buff icons (small translucent holographic icons)
```

## Boss血条（独立组件）

```
Top Center — Boss Status:
- Boss title "{{boss_name}} Lv.{{boss_level}}" in ornate frame
- Large red boss health bar at {{boss_hp_percent}}
- Buff/damage multiplier indicator "{{boss_buff}}" at right end of bar
- Gold ornate trim around the entire boss status area
```

## 使用说明

- `{{player_hp}}` 格式示例：`187654/313593 (60%)`
- `{{boss_hp_percent}}` 格式示例：`85%`
- `{{boss_buff}}` 格式示例：`x85` 或 `狂暴 x3`
