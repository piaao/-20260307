# 切图与 UI 资源清单（县令题材）

- 更新时间：2026-03-08T09:18:00+08:00
- 责任人：设计·山青
- 适配目标：Godot 4.x（`res://game/assets/ui/`）

## 命名与导出约束

- 命名格式：`ui_<模块>_<功能>_<状态>.png`
- 状态后缀：`normal | hover | pressed | disabled | empty`
- 分辨率策略：
  - 主界面底图：`1920x1080`
  - 按钮基准：`320x96`
  - 弹窗底板：`960x540`
  - 图标基准：`64x64`
- 九宫格建议：按钮、面板均保留 `12~16px` 安全边
- 文件约束：
  - 色彩空间 `sRGB`
  - 透明背景使用 `PNG`
  - 单文件建议小于 `1.5MB`

## 切图清单（首批）

| 资源名 | 尺寸 | 用途 | 命名示例 | 对应系统 |
|---|---|---|---|---|
| 主界面背景（白天） | 1920x1080 | 日间县衙主场景 | `ui_bg_main_day_normal.png` | 政务/建设 |
| 主界面背景（夜审） | 1920x1080 | 夜审主场景 | `ui_bg_main_night_normal.png` | 办案 |
| 开堂办案按钮 | 320x96 | 进入案件系统 | `ui_btn_case_start_normal.png` | 办案 |
| 政令面板按钮 | 320x96 | 打开政令面板 | `ui_btn_policy_open_normal.png` | 政令 |
| 建设面板按钮 | 320x96 | 打开建设面板 | `ui_btn_build_open_normal.png` | 建设 |
| 公告墙卡片底板 | 720x220 | 政令/公告信息承载 | `ui_panel_notice_normal.png` | 政令/民生 |
| 案件证据槽位 | 160x160 | 证据插槽容器 | `ui_slot_evidence_empty.png` | 办案 |
| 四维指标图标-民心 | 64x64 | HUD 指标图标 | `ui_icon_stat_people_normal.png` | 全局 |
| 四维指标图标-秩序 | 64x64 | HUD 指标图标 | `ui_icon_stat_order_normal.png` | 全局 |
| 四维指标图标-库银 | 64x64 | HUD 指标图标 | `ui_icon_stat_silver_normal.png` | 全局 |
| 四维指标图标-威望 | 64x64 | HUD 指标图标 | `ui_icon_stat_prestige_normal.png` | 全局 |
| 通用弹窗底板 | 960x540 | 系统提示/结算弹窗 | `ui_panel_modal_normal.png` | 全局 |

## Godot 落地路径建议

- 背景：`res://game/assets/ui/backgrounds/`
- 按钮：`res://game/assets/ui/buttons/`
- 面板：`res://game/assets/ui/panels/`
- 图标：`res://game/assets/ui/icons/`
- 案件专属：`res://game/assets/ui/case/`

## 一致性复核项（设计内审）

- 命名是否全部符合 `ui_<模块>_<功能>_<状态>.png`
- 尺寸是否命中基准（`320x96`/`64x64`/`960x540`/`1920x1080`），非基准项需单独备注（如 `160x160`、`720x220`）
- 资源是否可映射至四系统（政务/办案/政令/建设）
- 文案与路径是否可被开发直接引用

## 今日达成

- 已补齐尺寸规范与命名约束（满足日计划要求）
- 已补齐首批 12 项资源切图清单
- 已进入一致性复核模式，待开发接入后做第二轮命名校验
