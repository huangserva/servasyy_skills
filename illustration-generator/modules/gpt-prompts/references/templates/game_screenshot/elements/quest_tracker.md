# HUD Element: Quest Tracker

## 通用版本

```
Top Right — Quest Tracker:
- Current quest name
- Quest objective with progress
```

## 仙侠MMO版本

```
Top Right — Quest Tracker:
- Quest box with ornate gold border
- Main quest title: "{{quest_title}}" with ★ rarity indicator
- Subtitle: "{{quest_subtitle}}"
- Green progress arrow next to subtitle
- Optional: "追踪中" (Tracking) indicator
- Quest reward preview: EXP + item icons
```

### 任务标题模板库

史诗任务（红色标题）：
- `【史诗】挑战{{boss_name}}`
- `【史诗】拯救三界苍生`
- `【史诗】封印远古魔神`

主线任务（金色标题）：
- `【主线】前往{{location}}`
- `【主线】寻找{{npc_name}}`
- `【主线】收集{{item_name}} x{{count}}`

日常任务（蓝色标题）：
- `【日常】击败{{count}}只{{monster_name}}`
- `【日常】完成{{count}}次副本挑战`

## 赛博朋克版本

```
Top Center — Mission:
- Mission objective: "{{mission_objective}}" with waypoint distance "234m"
- Sub-objective checklist with completion markers
- Fixer name and reward amount displayed
- "NCPD 扫描中..." scanner progress bar
```

## 使用说明

- 仙侠任务追踪器通常在右上角，有华丽金色边框
- 赛博朋克的在顶部中央，简洁全息风格
- 任务副标题要有具体的行动描述，不要写"完成任务"
- 加绿色进度箭头能增加截图的真实感
