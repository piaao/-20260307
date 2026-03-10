# 串行执行规则

## 1. 启动前检查

每轮人工执行前，必须先检查：

- `manual_workflow/standups/YYYY-MM-DD.md`
- `automation/checks/planner/gate_check.json`
- 各角色 `manual_workflow/roles/<role>/context.md`
- 上游角色关键输出文件是否已更新

## 2. 角色读取边界

### PM
可读：全局状态、Git、闸门、评分、日报、全部角色输出摘要
可写：`work/pm/`

### Planner
可读：站会、PM 风险、玩家评测、策划相关文件
可写：`work/planner/`

### Player
可读：策划三件套、文案集、必要 PM 里程碑信息
可写：`work/player/`

### Designer
可读：策划定稿、玩家主要建议、开发接口约束
可写：`work/designer/`

### Developer
可读：策划定稿、设计约束、测试阻塞、音效接入点
可写：`work/developer/` 与 `game/`

### QA
可读：开发状态、策划规则、测试计划、已知问题
可写：`work/qa/`

### Sound
可读：策划事件/场景、设计风格、开发接入点
可写：`work/sound/`

## 3. 解锁规则

- 若策划闸门未通过：仅允许 `pm` / `planner`
- 若玩家评分 `< 8.0`：`designer` / `developer` / `qa` / `sound` 默认保持冻结，除非用户显式要求推进
- 若缺少 demo：`qa` 只做静态检查，不做运行态冒烟

## 4. 汇报规则

每个角色执行后，输出两层结果：

1. 角色正式产物更新
2. 面向用户的一段摘要

禁止只汇报过程句，不给结果。
