# 流程触发机制

## 目标

在不依赖后台 cron 的前提下，让多角色流程依据状态自动决定“下一位角色是谁”，并在主会话中持续串行推进。

## 触发原则

1. 每次角色完成后，立即触发一次“下一角色判定”。
2. 判定只基于单一事实源，不靠口头状态。
3. 任一时刻只允许一个激活角色。
4. 若命中冻结条件，则流程停在可执行的最近上游角色。

## 单一事实源

- 今日任务基线：`manual_workflow/standups/YYYY-MM-DD.md`
- 调度状态：`manual_workflow/state/runtime_state.json`
- 策划闸门：`automation/checks/planner/gate_check.json`
- 玩家评分：`work/player/score_report_v2.json`
- PM 调度板：`work/pm/delivery_status.md`

## 触发顺序

### A. PM 触发 Planner
当以下条件全部满足时：
- 今日 PM 基线已建立
- 当前没有 planner 正式产物
- 或 planner 需要继续修订

### B. Planner 触发 Player
当以下条件全部满足时：
- `master_design.md`
- `event_table_v1.md`
- `balance_sheet_v1.csv`
- `copy_deck_v1.md`
这四类输入存在，且策划闸门通过

### C. Player 触发下游
当玩家评分：
- `< 9.0`：回退给 Planner 继续修订
- `>= 9.0`：解锁 Designer / Developer / QA（QA 还需 demo）

### D. Developer 触发 QA
当以下条件全部满足时：
- 有 demo
- 有可测清单
- 有启动步骤
- 有版本标识

## 冻结条件

- 玩家评分 `< 9.0`：Designer / Developer / QA 默认冻结
- 缺 demo：QA 冻结
- 用户显式暂停某角色：该角色冻结

## 运行方式

每轮角色结束后，运行：

```bash
python3 manual_workflow/scripts/dispatch_next.py --apply
```

它会：
- 读取当前状态
- 判定下一角色
- 更新 `manual_workflow/state/runtime_state.json`
- 同步 `work/pm/delivery_status.md`
