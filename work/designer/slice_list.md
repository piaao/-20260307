# 切图与 UI 资源清单（县令题材）

- 更新时间：2026-03-08T13:28:00+08:00
- 责任人：设计·山青
- 适配目标：Godot 4.x（`res://game/assets/ui/`）
- 对齐依据：`work/pm/daily_plan_2026-03-08.md`、`work/planner/master_design.md`、`work/designer/main_visual_options.md`

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

## 模块命名映射（本轮补齐）

- `bg`：主界面背景与场景底图
- `btn`：可点击功能按钮
- `panel`：弹窗/信息承载底板
- `icon`：HUD 与状态图标
- `slot`：案件证据槽、道具槽

## 切图清单（首批 12 项）

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

## 与主视觉方案的对应关系（本轮补齐）

- A（青衙晨雾）优先资源：`ui_bg_main_day_normal.png`、`ui_panel_notice_normal.png`
- B（金灯夜审）优先资源：`ui_bg_main_night_normal.png`、`ui_slot_evidence_empty.png`
- C（市井朝会）优先资源：`ui_bg_main_day_normal.png`（后续新增市井变体）
- 四维指标图标（四项）为三方案通用资源，不单独分案

## 一致性复核项（设计内审）

- 命名是否全部符合 `ui_<模块>_<功能>_<状态>.png`
- 尺寸是否命中基准（`320x96`/`64x64`/`960x540`/`1920x1080`），非基准项需单独备注（如 `160x160`、`720x220`）
- 资源是否可映射至四系统（政务/办案/政令/建设）
- 文案与路径是否可被开发直接引用

## 一致性复核结果（2026-03-08 10:11）

- 命名一致性：通过（12/12）
- 尺寸口径一致性：通过（基准项 10，非基准项 2，均已备注）
- 系统映射一致性：通过（四系统全覆盖）
- 开发可接入性：通过（路径规范明确，可直接建目录导入）

## 本轮推进（2026-03-08 12:22）

- 新增交付批次标记：
  - `D1`（A 方案主流程接入批）
  - `D2`（B 方案办案压测批）
  - `D3`（C 方案经营展示批）
- 新增资源验收口径：
  - 文件名、尺寸、路径三项必须一次性通过；任一不符即退回修订
  - 关键交互资源（按钮、证据槽、公告板）必须同时提供 `normal` 与 `hover/empty` 对应状态
  - 导入 Godot 后需确认纹理缩放模式不导致文字边缘糊化
- 设计-开发交接最小清单：
  - 资源文件（PNG）
  - 对应命名表（本清单）
  - 使用位置说明（主界面/办案/政令/建设）

## 本轮推进（2026-03-08 13:28）

- 增补资源状态完整性要求（首批关键资源）：
  - 按钮类至少提供 `normal/hover/pressed/disabled`
  - 槽位类至少提供 `empty/normal`
  - 面板类至少提供 `normal`（若可交互再补 `hover`）
- 增补批次优先级映射：
  - D1：`ui_bg_main_day_normal.png`、`ui_btn_policy_open_*`、`ui_panel_notice_normal.png`
  - D2：`ui_bg_main_night_normal.png`、`ui_btn_case_start_*`、`ui_slot_evidence_*`
  - D3：建设与市井扩展图层及图标修饰项
- 增补交接验收动作（导入 Godot 前后各一次）：
  - 导入前：文件名/尺寸/路径三项脚本校验
  - 导入后：纹理过滤与缩放检查（避免文字边缘糊化）
  - 场景内：按钮点击热区与视觉边界一致性抽检

## 本轮推进（2026-03-09 09:12）

- 新增“草图阶段即锁定切图风险”的清单约束：
  - `ui_bg_main_day_normal.png` 增加遮罩源文件：`ui_bg_main_day_mask_overlay.png`（用于标注 UI 安全区）
  - `ui_bg_main_night_normal.png` 增加低对比回退稿：`ui_bg_main_night_fallback_normal.png`
  - `ui_panel_notice_normal.png` 增加高密文本版：`ui_panel_notice_dense_normal.png`
- 新增导出前检查项（设计自检）：
  - 背景图需附一张灰度可读性检查图（命名后缀 `_luma_check`）
  - 按钮四态图需做边界像素对齐，避免 Godot 导入后热区偏移
  - 图标四维组需统一视觉重心（中心偏移不超过 `±2px`）
- 新增 D1/D2/D3 资源就绪定义：
  - D1 就绪：主界面白天底图 + 政令按钮四态 + 公告板双版本（普通/高密）
  - D2 就绪：夜审底图（标准/回退）+ 办案按钮四态 + 证据槽 `empty/normal`
  - D3 就绪：建设按钮四态 + 市井扩展背景变体 + 图标修饰项
- 新增命名补充规则：
  - 遮罩辅助文件统一后缀 `_mask_overlay`
  - 可读性检查图统一后缀 `_luma_check`
  - 回退稿统一后缀 `_fallback_normal`

## 本轮推进（2026-03-09 09:45）

- 新增“切图就绪检查单”字段（用于 D1/D2/D3 统一验收）：
  - 文件命名：模块、功能、状态后缀齐全（含 `_mask_overlay` / `_luma_check` / `_fallback_normal`）
  - 尺寸基准：背景 `1920x1080`、按钮 `320x96`、图标 `64x64`、面板 `960x540`
  - 状态完整性：按钮四态、槽位双态、面板基础态
- 新增 D1/D2/D3 交付包最小集合：
  - D1：`ui_bg_main_day_normal.png` + `ui_bg_main_day_mask_overlay.png` + `ui_bg_main_day_luma_check.png` + `ui_btn_policy_open_*` + `ui_panel_notice_*`
  - D2：`ui_bg_main_night_normal.png` + `ui_bg_main_night_fallback_normal.png` + `ui_bg_main_night_luma_check.png` + `ui_btn_case_start_*` + `ui_slot_evidence_*`
  - D3：`ui_btn_build_open_*` + 市井扩展背景变体 + 图标修饰项（含可读性检查图）
- 新增交接退回条件（任一命中即退回）：
  - 命名与文档不一致
  - 尺寸偏离基准且未备注
  - 缺少 `_luma_check` 可读性检查图

## 本轮推进（2026-03-09 09:52）

- 新增 D1/D2/D3“联调排期字段”命名约束：
  - 联调优先版统一后缀 `_sync_v1`
  - 叙事增强版统一后缀 `_narrative_v1`
  - 交付冻结版统一后缀 `_lock`
- 新增关键资源批次映射（与主视觉 09:52 节点同步）：
  - D1：`ui_bg_main_day_sync_v1.png`、`ui_bg_main_day_narrative_v1.png`
  - D2：`ui_bg_main_night_sync_v1.png`、`ui_bg_main_night_fallback_normal.png`
  - D3：`ui_panel_notice_dense_normal.png`、市井扩展背景 `*_sync_v1`
- 新增导入抽检规则（开发联调前）：
  - 同名资源不同后缀版本必须共享相同锚点与热区矩形
  - `_sync_v1` 与 `_lock` 的尺寸与透明边界差异不得超过 `2px`
  - 夜审背景若启用回退稿，需同步保留 `_luma_check` 校验图
- 新增退回条件补充：
  - 缺失 `_sync_v1` 或 `_lock` 任一版本视为“不可联调交付”
  - 批次映射与 `main_visual_options.md` 节点不一致即退回

## 本轮推进（2026-03-09 10:08）

- 新增联调冻结规则（与 09:52 后缀体系衔接）：
  - 进入开发联调的背景资源默认使用 `_lock` 版本；`_sync_v1` 仅用于联调中间态比对
  - `_narrative_v1` 只允许叙事层改动，不得改变可交互区域透明边界与锚点
- 新增 D1/D2/D3 导包最小约束：
  - 每个批次必须同时包含：主资源图、`_luma_check`、对应遮罩或回退文件
  - 缺少任一校验文件视为“不可接入包”，直接退回设计补齐
- 新增夜审场景动效一致性检查（D2）：
  - `ui_bg_main_night_sync_v1.png` 与 `ui_bg_main_night_fallback_normal.png` 的按钮热区背景亮度差异不得超过 `8%`
  - 连续帧导出时，相邻关键帧亮度差不得超过 `6%`，避免 hover 识别抖动
- 新增公告板高密文本检查（D1/D3）：
  - `ui_panel_notice_dense_normal.png` 必须与普通版共享同一内容安全区
  - 文本区内边距与行距规则需与 `main_visual_options.md` 保持一致后才可标记 `_lock`
- 交接结论：
  - 当前切图命名、版本后缀、验收字段已覆盖“并行联调 + 回退”场景
  - 设计资源可按 `A -> B -> C` 批次继续交付，无阻塞项

## 今日达成

- 已补齐尺寸规范与命名约束（满足日计划要求）
- 已补齐首批 12 项资源切图清单
- 已补齐与主视觉 A/B/C 方案的一一映射
- 已完成一致性复核并转入“质量复核与风险监听”模式
- 已补充 13:28 资源状态完整性与 D1/D2/D3 交接验收动作
- 已在 09:12 增补草图阶段切图风险控制与资源就绪定义
- 已在 09:45 增补切图就绪检查单与交付包最小集合
- 已在 09:52 增补联调排期字段、版本后缀规范与导入抽检规则
