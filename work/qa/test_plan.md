# 测试计划（2026-03-09）

- 更新时间：2026-03-09T10:05:08+08:00
- 对齐来源：`work/pm/daily_plan_2026-03-08.md`
- 门禁状态：`automation/checks/planner/gate_check.json` → `passed = true`
- 测试基线：`master@0b2cc62`
- 今日角色目标：维护测试计划与回归入口；在可行范围内先完成冒烟。

## 测试范围（按 PM 日计划映射）
1. 核心链路：政务 → 办案 → 政令 → 建设（单日闭环）。
2. 规则一致性：官阶解锁、资源结算、案件等级解锁。
3. 策划还原度：`master_design.md`、`event_table_v1.md`、`balance_sheet_v1.csv` 与实现映射一致。
4. 交付联动：设计切图规范、音效任务清单、开发可测功能清单的接入完整性。

## 本轮可行范围冒烟（已执行）
1. 工程可识别性：`game/project.godot` 存在且主场景为 `res://scenes/main.tscn`。
2. 启动入口完整性：`game/scenes/main.tscn` 已挂载 `res://scripts/game_flow.gd`。
3. 配置依赖可达性：`game/data/policy.json`、`game/data/buildings.json`、`game/data/cases.json` 均存在。
4. 策划依赖可达性：`work/planner/event_table_v1.md`、`work/planner/balance_sheet_v1.csv` 均存在。
5. 运行环境核验：当前主机未发现 `godot`/`godot4` 可执行，运行态冒烟暂不可执行。

## 当前阻塞与等待项
- B1（阻断）：运行环境缺少 Godot 可执行程序，无法执行运行态冒烟与日志采集。
- B2（次阻塞）：`work/developer/dev_status.md` 缺少“可测功能清单 + 启动步骤 + 已知问题”。
- W1（等待确认）：PM 未明确“测试窗口冻结”口径；已先记录临时基线 `master@0b2cc62`。

## 解锁条件（Triggers）
- T1：提供可用 Godot 运行器（`godot` 或 `godot4`）及启动命令。
- T2：开发补齐 `work/developer/dev_status.md` 的可测边界信息。
- T3：PM 确认测试窗口冻结版本（沿用 `master@0b2cc62` 或指定新基线）。

## 解锁后执行顺序
1. 15 分钟运行态冒烟：启动、进入主场景、执行一次“政务→办案→政令→建设”闭环。
2. 规则抽测：官阶、资源结算、案件等级解锁规则。
3. 还原度核对：策划条目与运行行为逐项比对并记录偏差。
4. 结果沉淀：缺陷分级（阻断/严重/一般/建议）+ 复现步骤 + 修复建议。
