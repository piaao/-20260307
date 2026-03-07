# 项目经理任务看板

- 更新时间：2026-03-07T23:41:40+08:00

## Git 状态
```
## master...origin/master
 M automation/checks/developer/godot_project_check.json
 M automation/checks/planner/design_status.md
 M automation/checks/planner/gate_check.json
 M automation/checks/planner/gate_check.md
 M automation/logs/planner.log
 M automation/logs/player.log
 M automation/logs/pm.log
 D automation/outputs/designer/main_visual_options.md
 D automation/outputs/designer/slice_list.md
 D automation/outputs/developer/dev_status.md
 D automation/outputs/developer/godot_project_check.json
 D automation/outputs/planner/design_day1.md
 M automation/outputs/planner/design_status.md
 M automation/outputs/planner/gate_check.json
 M automation/outputs/planner/gate_check.md
 D automation/outputs/planner/master_design.md
 D automation/outputs/player/score_report.json
 D automation/outputs/player/score_report.md
 D automation/outputs/player/score_report_v2.json
 D automation/outputs/player/score_report_v2.md
 D automation/outputs/pm/risk_log.md
 D automation/outputs/qa/test_plan.md
 D automation/outputs/qa/test_result.md
 D automation/outputs/sound/mood_board.md
 D automation/outputs/sound/sfx_task_list.md
 M automation/reports/daily_report.md
 M automation/reports/dashboard.md
 M automation/reports/git_activity.md
 D automation/reports/project_schedule.md
 M automation/state/status.json
 D game/scenes/main.tscn
 D game/scripts/game_flow.gd
 M work/designer/main_visual_options.md
 M work/designer/slice_list.md
 M work/developer/dev_status.md
 M work/planner/master_design.md
 M work/player/score_report.json
 M work/player/score_report_v2.json
 M work/player/score_report_v2.md
 M work/pm/commit_frequency_check.json
 M work/pm/risk_log.md
 M work/qa/test_plan.md
 M work/qa/test_result.md
 M work/sound/mood_board.md
 M work/sound/sfx_task_list.md
?? .clawdhub/
?? .openclaw/
?? AGENTS.md
?? BOOTSTRAP.md
?? HEARTBEAT.md
?? IDENTITY.md
?? MEMORY.md
?? SOUL.md
?? TOOLS.md
?? USER.md
?? automation/bin/run_role_work.sh
?? automation/bin/work_runner.py
?? automation/logs/all.cron.log
?? automation/logs/designer.cron.log
?? automation/logs/designer.log
?? automation/logs/designer.work.log
?? automation/logs/developer.cron.log
?? automation/logs/developer.log
?? automation/logs/developer.work.log
?? automation/logs/planner.cron.log
?? automation/logs/planner.work.log
?? automation/logs/player.cron.log
?? automation/logs/player.work.log
?? automation/logs/pm.cron.log
?? automation/logs/qa.cron.log
?? automation/logs/qa.log
?? automation/logs/sound.cron.log
?? automation/logs/sound.log
?? automation/state/locks/designer.lock
?? automation/state/locks/designer.work.lock
?? automation/state/locks/developer.lock
?? automation/state/locks/developer.work.lock
?? automation/state/locks/planner.lock
?? automation/state/locks/planner.work.lock
?? automation/state/locks/player.lock
?? automation/state/locks/player.work.lock
?? automation/state/locks/pm.work.lock
?? mac_links.db
?? memory/
?? skills/
?? work/developer/godot_structure_plan.md
?? work/planner/balance_sheet_v1.csv
?? work/planner/event_table_v1.md
```

## 最近提交
```
44f97ed chore: remove unused image and temporary godot scaffold files
2c16747 docs(pm): formalize github commit cadence policy in markdown
33cd8f5 feat(pm): enforce github commit cadence policy and auto frequency checks
c5e5fcc refactor: separate role workspaces from automation checks and normalize godot layout
0344be4 fix: add per-role lock to prevent concurrent cron overwrite
4ae17a5 feat: enforce planning quality gate and evidence-based player evaluation
7abdf9c docs: add gap analysis against reference planning doc
d62b220 feat(pm): generate daily report with schedule variance checks
```

## 关键职责
1. 提交频率监管（2h规则）
2. 里程碑偏差管理
3. 风险升级与日报同步
