# Godot 工程结构与策划映射（V1.2）

- 更新时间：2026-03-09T10:11:00+08:00
- 责任角色：开发·神机
- 对齐来源：`work/planner/master_design.md`（V1.4）

## 一、工程结构（当前已落地）

- `res://project.godot`（文件：`game/project.godot`）
- `res://scenes/main.tscn`（文件：`game/scenes/main.tscn`）
- `res://scripts/game_flow.gd`（文件：`game/scripts/game_flow.gd`）
- `res://scripts/state_center.gd`（文件：`game/scripts/state_center.gd`）
- `res://data/policy.json`（文件：`game/data/policy.json`）
- `res://data/buildings.json`（文件：`game/data/buildings.json`）
- `res://data/cases.json`（文件：`game/data/cases.json`）

## 二、核心循环映射（策划→实现）

1. 政务处理（每日自然波动）
   - 入口：`StateCenter.apply_natural_tick()`
   - 参数：民心-2、库银+50、秩序-1、威望0

2. 开堂办案（CASE 结算）
   - 数据：`res://data/cases.json`
   - 入口：`game_flow._resolve_case(case_id, success)`

3. 颁布政令（即时+延迟收益）
   - 数据：`res://data/policy.json` + `work/planner/balance_sheet_v1.csv`
   - 入口：`game_flow._apply_policy(policy_id)`
   - 延迟：`game_flow._schedule_policy_delayed(policy_id)`

4. 建设县城（升级+周收益）
   - 数据：`res://data/buildings.json` + `work/planner/balance_sheet_v1.csv`
   - 入口：`game_flow._apply_build(build_id)`
   - 周结算增益：`game_flow._collect_weekly_build_bonus(treasury_net)`

## 三、统一状态中心约束

- 单一状态源：四维指标统一在 `StateCenter.metrics`
- 单一结算口：统一经 `apply_delta(source, delta)`
- 动态红线：`StateCenter.set_thresholds()` 注入红线规则
- 历史追踪：`history` 保留来源、变更、快照
- 延迟队列：`schedule_delta()` + `advance_day()` 统一处理

## 四、周/月循环与晋升映射

1. 周结算（每 7 天）
   - 入口：`game_flow._apply_weekly_settlement()`
   - 输出：周财政净增长、建筑周收益、官阶变化

2. 月结算（每 28 天）
   - 入口：`game_flow._apply_monthly_settlement()`
   - 输出：月报快照（官阶、近4周财政走势、指标快照）

3. 官阶晋升
   - 八品：民心>=60 且 秩序>=55
   - 七品：连续两周财政净增长>0
   - 判定函数：`game_flow._evaluate_rank_tier()`

## 五、配置驱动策略

- 优先读取平衡表的 `formula_or_rule` 并覆盖默认配置。
- 政令规则：`instant` + `dayN` 延迟收益。
- 建筑规则：升级成本 + `week_tax+%` 周收益规则。
- 阈值规则：`heart/treasury/order/prestige` 红线注入状态中心。

## 六、与策划一致性检查（V1.4）

- 四大日循环模块：一致
- 事件调度口径（权重/冷却/条件）：一致
- 政令 3日/7日滞后收益：一致
- 周/月结算接口：已补齐
- 官阶晋升规则：已落地

## 七、当前稳定性复核结论

- 工程结构稳定：通过
- 路径与资源引用稳定：通过
- 配置可解析：通过
- 引擎内运行冒烟：待执行（环境缺少 Godot 可执行）

## 八、下一版（V1.3）

1. 审案系统面板拆分：`case_panel.tscn` + `case_controller.gd`
2. 政令/建设面板拆分：`policy_panel.tscn`、`build_panel.tscn`
3. 案件触发条件与事件选项（A/B）外部输入接口
4. QA 固定随机种子与回归快照导出（CSV/JSON）
