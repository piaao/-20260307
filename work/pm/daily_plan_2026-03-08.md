# 2026-03-08 日计划（七角色）

## 总目标
- 完成古代县令项目当日可验收产出，形成可追溯文件与版本记录。
- 通过质量闸门并维持玩家评分 >= 8.0。

## 角色任务与完成标准

### 1) 策划·阿席
- 今日任务：完善主策划案、补齐案件参数、政令曲线、实施映射与验收标准。
- 完成标准：
  - `work/planner/master_design.md` 通过闸门；
  - `work/planner/event_table_v1.md` 与 `work/planner/balance_sheet_v1.csv` 有有效更新；
  - 文档含责任人、截止时间、交付清单。

### 2) 玩家·风评官
- 今日任务：按 8 画像×10维模型完成评测并给出证据链。
- 完成标准：
  - `work/player/score_report_v2.md` 与 `.json` 更新；
  - 评分 >= 8.0，若不足需给出三条可执行整改建议。

### 3) 设计·山青
- 今日任务：主视觉3方向细化并更新切图规范。
- 完成标准：
  - `work/designer/main_visual_options.md` 更新且包含 A/B/C 方案；
  - `work/designer/slice_list.md` 包含尺寸与命名约束。

### 4) 开发·神机
- 今日任务：稳定 Godot 工程结构并推进核心循环脚本映射。
- 完成标准：
  - `game/project.godot` 可识别；
  - `work/developer/dev_status.md` 更新；
  - `work/developer/godot_structure_plan.md` 与策划映射一致。

### 5) 项目经理·纪衡
- 今日任务：把控提交频率、风险升级、日报完整性。
- 完成标准：
  - `work/pm/commit_frequency_check.json` 更新；
  - `work/pm/risk_log.md`、`automation/reports/daily_report.md` 更新；
  - 无 2h/4h 提交违规未处理项。

### 6) 测试·素问
- 今日任务：维护测试计划与回归入口，等待 demo 后执行冒烟。
- 完成标准：
  - `work/qa/test_plan.md`、`work/qa/test_result.md` 更新时间刷新；
  - 明确阻塞项与下一步测试触发条件。

### 7) 音效·鸣泉
- 今日任务：补齐场景音效任务列表与优先级。
- 完成标准：
  - `work/sound/mood_board.md`、`work/sound/sfx_task_list.md` 更新；
  - 标注高优先级 SFX 与依赖关系。

## 运行原则
- 各角色按职责独立推进；
- 未完成前持续定时执行；
- 完成后改为“质量复核与风险监听”模式。
