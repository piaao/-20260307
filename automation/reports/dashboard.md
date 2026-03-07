# 角色后台监控面板

- 项目：古代县令模拟器
- 最近刷新：2026-03-07T22:40:21+08:00

| 角色 | 状态 | 最近运行 | 最近产出 | 备注 |
|---|---|---|---|---|
| 策划·阿席 | completed | 2026-03-07T22:40:01+08:00 | automation/outputs/planner/design_day1.md | 已更新策划草案巡检文件 |
| 玩家·风评官 | completed | 2026-03-07T22:40:01+08:00 | automation/outputs/player/score_report.json, automation/outputs/player/score_report.md | 评分 7.4（需迭代） |
| 设计·山青 | completed | 2026-03-07T22:40:01+08:00 | automation/outputs/designer/main_visual_options.md, automation/outputs/designer/slice_list.md | 已更新主视觉与切图清单 |
| 开发·神机 | completed | 2026-03-07T22:40:01+08:00 | automation/outputs/developer/dev_status.md, automation/outputs/developer/godot_project_check.json | Godot 工程已检测 |
| 项目经理·纪衡 | completed | 2026-03-07T22:40:21+08:00 | automation/reports/git_activity.md, automation/outputs/pm/risk_log.md, automation/reports/daily_report.md | 已更新 Git 活动、风险日志与日报（含排期偏差） |
| 测试·素问 | completed | 2026-03-07T22:40:01+08:00 | automation/outputs/qa/test_plan.md, automation/outputs/qa/test_result.md | 测试计划已更新，等待 demo |
| 音效·鸣泉 | completed | 2026-03-07T22:40:01+08:00 | automation/outputs/sound/mood_board.md, automation/outputs/sound/sfx_task_list.md | 音效 mood board 已更新 |

## 检查规则
- 角色完成必须有对应产出文件或 Git 提交记录。
- 若角色状态为 completed 但最近产出为空，判定为异常。
- 日报前执行一次 `all` 全量巡检。
