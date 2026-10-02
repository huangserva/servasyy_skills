# HUD Element: Chat Box

## 通用版本

```
Bottom Left — Chat Box:
- Semi-transparent chat window
- System messages and player chat visible
```

## 仙侠MMO版本

```
Bottom Left — Chat Box:
- Red [系统] (System) messages:
  - "你获得了【{{item_name}}】" (You obtained item)
  - "{{boss_name}}释放了【{{boss_skill}}】" (Boss cast skill)
  - "注意躲避!" (Dodge warning!)
- Green [世界] (World Chat) player messages:
  - "[{{player_1}}]: {{message_1}}"
  - "[{{player_2}}]: {{message_2}}"
  - "[{{player_3}}]: {{message_3}}"
- Chat tab buttons: 世界(World)/队伍(Team)/帮会(Guild)/附近(Nearby)
```

### 消息模板库

Boss战常用系统消息：
- `你获得了【齐天战甲】` — 掉落获得
- `你获得了大量经验 (x2)` — 经验加倍
- `{{boss_name}}释放了【{{skill_name}}】` — Boss技能释放
- `注意躲避!` — 闪避提示
- `全屏AOE即将到来!` — 大招预警

世界频道常用消息：
- `[逍遥子]: 加油！少侠!` — 助威
- `[白衣剑客]: 这BOSS太强了!` — 吐槽
- `[紫霞仙子]: 美人助你一臂之力!` — 玩家互动
- `[剑圣无双]: 第一次过这个本，求带!` — 求组
- `[花间一壶酒]: 坐标(235,178)刷新了稀有怪!` — 资源分享

## 赛博朋克版本

```
Bottom Left — Comm Link:
- Holographic translucent message feed
- [NCPD] police scanner alerts in yellow
- [FIXER] mission updates in cyan
- [NET] netrunner messages in green with slight glitch effect
- Incoming call notification overlay
```

## 使用说明

- 聊天框是让截图"活"起来的利器，3-4条消息最佳
- 系统消息用红色/黄色（重要），世界频道用绿色（轻松）
- 赛博朋克聊天要有glitch/全息效果，不是普通文字框
- 不要塞太多消息（>6条），会遮挡游戏画面
