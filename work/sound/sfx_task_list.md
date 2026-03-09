# 音效任务清单

- 更新时间：2026-03-09T10:22:00+08:00
- 来源计划：`work/pm/daily_plan_2026-03-08.md`
- 执行批次：`cron:35372550-65e5-4aa7-bc02-6df3820cdd84`

| 编号 | 文件名 | 场景 | 优先级 | 触发事件 | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| SFX-01 | sfx_court_gavel.wav | 审案 | 高 | 判决确认/开堂 | 事件表字段冻结 | 待制作 |
| SFX-02 | sfx_scroll_open.wav | 政务 | 高 | 卷宗展开/信息面板打开 | UI 交互事件命名 | 待制作 |
| SFX-03 | sfx_city_crowd_loop.wav | 市井 | 中 | 主城驻留循环 | 场景分层与昼夜参数 | 待制作 |
| SFX-04 | sfx_policy_confirm.wav | 政令 | 高 | 政令发布成功 | 政令状态机稳定 | 待制作 |
| SFX-05 | sfx_court_drum_hit.wav | 审案 | 高 | 开堂/流程节点推进 | 审案流程事件映射 | 待制作 |
| SFX-06 | sfx_edict_gong.wav | 政令 | 高 | 政令宣告/全局提示 | 全局广播通道 | 待制作 |
| SFX-07 | sfx_build_complete_fanfare.wav | 建设 | 高 | 建筑完工结算 | 建设完成回调 | 待制作 |
| SFX-08 | sfx_market_vendor_call_01.wav | 市井 | 中 | 市井随机点缀 | 区域随机池配置 | 待制作 |
| SFX-09 | sfx_brush_write_short.wav | 审案/政务 | 中 | 文书确认/签发 | 输入确认事件统一 | 待制作 |
| SFX-10 | sfx_ui_wood_click.wav | 通用UI | 中 | 按钮点击（古风皮肤） | UI 皮肤上线 | 待制作 |

## 本日高优先级交付包（P0）
- SFX-01 `sfx_court_gavel.wav`
- SFX-02 `sfx_scroll_open.wav`
- SFX-04 `sfx_policy_confirm.wav`
- SFX-05 `sfx_court_drum_hit.wav`
- SFX-06 `sfx_edict_gong.wav`
- SFX-07 `sfx_build_complete_fanfare.wav`

## 依赖关系说明
- 先完成审案与政令的确认类 SFX（影响核心循环反馈）。
- 建设完工音效与奖励结算动画同步（避免先声后画错位）。
- 市井环境循环在场景分层稳定后再混音定版。