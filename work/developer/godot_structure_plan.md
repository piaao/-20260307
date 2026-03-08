# Godot 工程结构与策划映射（V1.1）

- 更新时间：2026-03-08T09:24:58+08:00
- 责任角色：开发·神机
- 对齐来源：`work/planner/master_design.md`（V1.3）

## 一、工程结构（当前已落地）

- `res://project.godot`（文件：`game/project.godot`）
- `res://scenes/main.tscn`（文件：`game/scenes/main.tscn`）
- `res://scripts/game_flow.gd`（文件：`game/scripts/game_flow.gd`）
- `res://scripts/state_center.gd`（文件：`game/scripts/state_center.gd`）
- `res://data/policy.json`（文件：`game/data/policy.json`）
- `res://data/buildings.json`（文件：`game/data/buildings.json`）
- `res://data/cases.json`（文件：`game/data/cases.json`）

## 二、核心循环映射（策划→实现）

1. 政务处理
   - 策划定义：每日自然波动（民心-2、库银+50、秩序-1、威望0）
   - 代码入口：`StateCenter.apply_natural_tick()`

2. 开堂办案
   - 策划定义：CASE-001~012 成败奖惩
   - 数据来源：`res://data/cases.json`
   - 代码入口：`game_flow._resolve_case(case_id, success)`

3. 颁布政令
   - 策划定义：POL001~006 即时收益与成本
   - 数据来源：`res://data/policy.json`
   - 代码入口：`game_flow._apply_policy(policy_id)`

4. 建设县城
   - 策划定义：BLD001~005 升级成本与收益
   - 数据来源：`res://data/buildings.json`
   - 代码入口：`game_flow._apply_build(build_id)`

## 三、统一状态中心约束

- 单一状态源：四维指标统一在 `StateCenter.metrics` 中维护
- 单一结算口：所有变化经 `apply_delta(source, delta)` 写入
- 阈值告警：每步后执行 `check_thresholds()`
- 历史追踪：`history` 保留来源、变更、快照用于回归

## 四、与策划映射一致性检查

- 与主策划文档一致：四大循环模块与四维指标一致
- 与平衡表一致：POL/BLD/CASE ID 全量覆盖并可直接驱动
- 与接口约束一致：配置源限定 JSON，逻辑统一状态中心

## 五、稳定性复核结论

- 工程结构稳定：通过
- 路径与资源引用稳定：通过
- 配置可解析：通过
- 引擎内运行冒烟：待执行（环境缺少 Godot 可执行）

## 六、下一版规划（V1.2）

1. 接入 `event_table_v1` 事件调度与权重冷却逻辑
2. 引入延迟收益队列（day3/day7）
3. 增加周/月结算接口与官阶晋升判定
4. 增加 QA 固定种子回归入口
