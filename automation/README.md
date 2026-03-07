# 角色后台自动化框架（首版）

## 目录
- `configs/roles.json`：7 角色配置与目标产出路径
- `bin/role_runner.py`：统一后台 runner（支持 `--role <id|all>`）
- `state/status.json`：每个角色最近运行状态
- `reports/dashboard.md`：监控面板（自动生成）
- `reports/git_activity.md`：项目经理 Git 巡检报告
- `logs/*.log`：角色运行日志
- `outputs/<role>/`：角色落地产物

## 使用
```bash
python3 automation/bin/role_runner.py --role all
python3 automation/bin/role_runner.py --role planner
```

## 角色 id
- planner
- player
- designer
- developer
- pm
- qa
- sound

## 验收规则
1. 角色状态 `completed` 必须对应产出文件。
2. 开发角色必须检查 `project.godot` 是否存在。
3. 日报前执行一次 `--role all`，确保监控面板和 Git 活动更新。
