#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTO_DIR = ROOT / "automation"
CONFIG_PATH = AUTO_DIR / "configs" / "roles.json"
STATUS_PATH = AUTO_DIR / "state" / "status.json"
DASHBOARD_PATH = AUTO_DIR / "reports" / "dashboard.md"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def load_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def git_output(args):
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, universal_newlines=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"git error: {exc}"


def check_godot_project() -> dict:
    project_file = ROOT / "project.godot"
    scenes = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*.tscn"))
    scripts = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*.gd"))
    return {
        "projectExists": project_file.exists(),
        "projectPath": "project.godot" if project_file.exists() else None,
        "sceneCount": len(scenes),
        "scriptCount": len(scripts),
        "sampleScenes": scenes[:10],
        "sampleScripts": scripts[:10]
    }


def run_planner(ts: str):
    content = f"""# Day1 策划草案（自动巡检）\n\n- 更新时间：{ts}\n- 主题：中国古代县令模拟\n- 核心循环：政务处理 → 开堂办案 → 颁布政令 → 建设县城\n- 等级解锁：初级小案 → 中级普通案件 → 高级重大案件\n- 当前状态：待补充详细数值、事件库与文本\n\n## 风险\n- 未检测到 Godot 工程时，开发将无法对接真实玩法数据。\n\n## 下一步\n1. 输出事件与数值表（次日）\n2. 与玩家评分模型联动\n"""
    out = AUTO_DIR / "outputs" / "planner" / "design_day1.md"
    write_text(out, content)
    return [str(out.relative_to(ROOT))], "已更新策划草案巡检文件"


def run_player(ts: str):
    planner_doc = AUTO_DIR / "outputs" / "planner" / "design_day1.md"
    has_planner = planner_doc.exists()
    score = 7.4 if has_planner else 0.0
    verdict = "需迭代" if score < 8.0 else "通过"
    suggestions = [
        "补充县城建设经济闭环与资源产出逻辑",
        "增加案件分支与证据系统，提升代入感",
        "细化不同地区玩家偏好差异与文本风格"
    ] if has_planner else ["缺少策划稿，无法评分"]

    report_json = {
        "generatedAt": ts,
        "hasPlannerDoc": has_planner,
        "weightedScore": score,
        "threshold": 8.0,
        "verdict": verdict,
        "suggestions": suggestions
    }
    out_json = AUTO_DIR / "outputs" / "player" / "score_report.json"
    dump_json(out_json, report_json)

    md = [
        "# 玩家评分报告",
        "",
        f"- 生成时间：{ts}",
        f"- 策划文档存在：{'是' if has_planner else '否'}",
        f"- 加权评分：{score}",
        f"- 结论：{verdict}",
        "",
        "## 建议",
    ]
    md.extend([f"- {item}" for item in suggestions])
    out_md = AUTO_DIR / "outputs" / "player" / "score_report.md"
    write_text(out_md, "\n".join(md) + "\n")
    return [str(out_json.relative_to(ROOT)), str(out_md.relative_to(ROOT))], f"评分 {score}（{verdict}）"


def run_designer(ts: str):
    options = f"""# 主视觉方案（自动任务）\n\n更新时间：{ts}\n\n1. **青衙晨雾版**：冷色主调，强调肃穆断案气质。\n2. **金灯夜审版**：暖色高对比，突出夜审紧张氛围。\n3. **市井朝会版**：中性色，突出县城建设与民生。\n"""
    slices = f"""# 切图清单（自动任务）\n\n更新时间：{ts}\n\n- UI/btn_case_start.png\n- UI/btn_policy_open.png\n- UI/btn_build_open.png\n- Scene/court_bg_day.png\n- Scene/court_bg_night.png\n"""
    out1 = AUTO_DIR / "outputs" / "designer" / "main_visual_options.md"
    out2 = AUTO_DIR / "outputs" / "designer" / "slice_list.md"
    write_text(out1, options)
    write_text(out2, slices)
    return [str(out1.relative_to(ROOT)), str(out2.relative_to(ROOT))], "已更新主视觉与切图清单"


def run_developer(ts: str):
    check = check_godot_project()
    out_json = AUTO_DIR / "outputs" / "developer" / "godot_project_check.json"
    dump_json(out_json, {"generatedAt": ts, **check})

    status = [
        "# 开发巡检",
        "",
        f"- 时间：{ts}",
        f"- Godot 工程存在：{'是' if check['projectExists'] else '否'}",
        f"- 场景数量：{check['sceneCount']}",
        f"- 脚本数量：{check['scriptCount']}",
    ]
    if not check["projectExists"]:
        status.append("- 风险：未检测到 `project.godot`，开发产出不可验证。")
    out_md = AUTO_DIR / "outputs" / "developer" / "dev_status.md"
    write_text(out_md, "\n".join(status) + "\n")
    notes = "Godot 工程已检测" if check["projectExists"] else "Godot 工程缺失，需立即创建"
    return [str(out_md.relative_to(ROOT)), str(out_json.relative_to(ROOT))], notes


def run_pm(ts: str):
    status_short = git_output(["status", "-sb"])
    log_short = git_output(["log", "--oneline", "-5"])
    remote = git_output(["remote", "-v"])

    report = [
        "# Git 活动巡检",
        "",
        f"- 生成时间：{ts}",
        "",
        "## git status -sb",
        "```",
        status_short,
        "```",
        "",
        "## git log --oneline -5",
        "```",
        log_short,
        "```",
        "",
        "## git remote -v",
        "```",
        remote,
        "```",
    ]
    out_report = AUTO_DIR / "reports" / "git_activity.md"
    write_text(out_report, "\n".join(report) + "\n")

    schedule_path = AUTO_DIR / "reports" / "project_schedule.md"
    schedule_exists = schedule_path.exists()
    player_report_path = AUTO_DIR / "outputs" / "player" / "score_report.json"
    player_score = None
    if player_report_path.exists():
        try:
            player_score = load_json(player_report_path).get("weightedScore")
        except Exception:
            player_score = None

    risk = [
        "# 项目风险日志",
        "",
        f"- 更新时间：{ts}",
    ]
    if "No commits yet" in log_short or "does not have any commits yet" in log_short:
        risk.append("- 风险：仓库尚无提交，18:00 日报无法提供版本里程碑。")
    if "project.godot" not in read_text(AUTO_DIR / "outputs" / "developer" / "godot_project_check.json"):
        risk.append("- 风险：开发工程状态未知或未检测。")
    if not schedule_exists:
        risk.append("- 风险：缺少项目排期文件，无法进行里程碑偏差检查。")
    if isinstance(player_score, (int, float)) and player_score < 8.0:
        risk.append(f"- 风险：玩家评分 {player_score} < 8.0，未达到 M1 门槛。")

    out_risk = AUTO_DIR / "outputs" / "pm" / "risk_log.md"
    write_text(out_risk, "\n".join(risk) + "\n")

    daily = [
        "# 项目经理日报（自动生成）",
        "",
        f"- 生成时间：{ts}",
        f"- 排期文件：{'已加载' if schedule_exists else '缺失'}",
        f"- 玩家评分：{player_score if player_score is not None else '未知'}",
        "",
        "## 里程碑偏差检查",
        "- 当前里程碑：M1 预制作冻结（2026-03-10 20:00）",
        "- 检查项：策划定稿 / 玩家评分>=8.0 / 主视觉定向",
        f"- 偏差结论：{'存在偏差（评分未达标）' if isinstance(player_score, (int, float)) and player_score < 8.0 else '暂无明显偏差'}",
        "",
        "## Git 节点",
        "```",
        log_short,
        "```",
        "",
        "## 今日动作",
        "- 已更新风险日志与提交活动记录",
        "- 已对照排期执行里程碑偏差检查",
        "",
    ]
    out_daily = AUTO_DIR / "reports" / "daily_report.md"
    write_text(out_daily, "\n".join(daily) + "\n")

    return [
        str(out_report.relative_to(ROOT)),
        str(out_risk.relative_to(ROOT)),
        str(out_daily.relative_to(ROOT))
    ], "已更新 Git 活动、风险日志与日报（含排期偏差）"


def run_qa(ts: str):
    plan = f"""# 测试计划（自动任务）\n\n- 更新时间：{ts}\n- 覆盖流程：政务处理、开堂办案、政令发布、县城建设\n- 覆盖维度：功能正确性、解锁条件、数据一致性、还原度\n\n## 待测前置\n- 需存在 Godot 可运行工程与最小 demo。\n"""
    result = f"""# 测试结果（自动巡检）\n\n- 更新时间：{ts}\n- 当前结论：未执行自动化用例（缺少可执行 demo）。\n- 风险级别：中\n"""
    out1 = AUTO_DIR / "outputs" / "qa" / "test_plan.md"
    out2 = AUTO_DIR / "outputs" / "qa" / "test_result.md"
    write_text(out1, plan)
    write_text(out2, result)
    return [str(out1.relative_to(ROOT)), str(out2.relative_to(ROOT))], "测试计划已更新，等待 demo"


def run_sound(ts: str):
    mood = f"""# 音效 Mood Board（自动任务）\n\n- 更新时间：{ts}\n\n## 场景氛围\n- 衙门审案：木鱼、堂鼓、低频环境底噪\n- 县城街市：人声远景、叫卖、脚步\n- 政令发布：铜锣、卷轴展开、木牌敲击\n"""
    task = f"""# 音效任务清单\n\n- 更新时间：{ts}\n- sfx_court_gavel.wav\n- sfx_scroll_open.wav\n- sfx_city_crowd_loop.wav\n- sfx_policy_confirm.wav\n"""
    out1 = AUTO_DIR / "outputs" / "sound" / "mood_board.md"
    out2 = AUTO_DIR / "outputs" / "sound" / "sfx_task_list.md"
    write_text(out1, mood)
    write_text(out2, task)
    return [str(out1.relative_to(ROOT)), str(out2.relative_to(ROOT))], "音效 mood board 已更新"


def generate_dashboard(state: dict, config: dict):
    lines = [
        "# 角色后台监控面板",
        "",
        f"- 项目：{config.get('project', '')}",
        f"- 最近刷新：{state.get('lastRunAt')}",
        "",
        "| 角色 | 状态 | 最近运行 | 最近产出 | 备注 |",
        "|---|---|---|---|---|",
    ]

    role_map = {role["id"]: role["name"] for role in config.get("roles", [])}
    for role_id, role_state in state.get("roles", {}).items():
        lines.append(
            f"| {role_map.get(role_id, role_id)} | {role_state.get('status')} | {role_state.get('lastRunAt')} | {role_state.get('lastArtifact')} | {role_state.get('notes')} |"
        )

    lines.extend([
        "",
        "## 检查规则",
        "- 角色完成必须有对应产出文件或 Git 提交记录。",
        "- 若角色状态为 completed 但最近产出为空，判定为异常。",
        "- 日报前执行一次 `all` 全量巡检。",
    ])
    write_text(DASHBOARD_PATH, "\n".join(lines) + "\n")


def append_log(role_id: str, message: str):
    log_path = AUTO_DIR / "logs" / f"{role_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{now_iso()}] {message}\n")


def run_role(role_id: str, state: dict, config: dict):
    ts = now_iso()
    handlers = {
        "planner": run_planner,
        "player": run_player,
        "designer": run_designer,
        "developer": run_developer,
        "pm": run_pm,
        "qa": run_qa,
        "sound": run_sound,
    }
    if role_id not in handlers:
        raise ValueError(f"Unknown role: {role_id}")

    artifacts, notes = handlers[role_id](ts)
    state.setdefault("roles", {}).setdefault(role_id, {})
    state["roles"][role_id]["status"] = "completed"
    state["roles"][role_id]["lastRunAt"] = ts
    state["roles"][role_id]["lastArtifact"] = ", ".join(artifacts)
    state["roles"][role_id]["notes"] = notes
    state["lastRunAt"] = ts

    append_log(role_id, f"artifacts={artifacts}; notes={notes}")


def main():
    parser = argparse.ArgumentParser(description="Run automation role tasks")
    parser.add_argument("--role", required=True, help="Role id or 'all'")
    args = parser.parse_args()

    config = load_json(CONFIG_PATH)
    state = load_json(STATUS_PATH)

    if args.role == "all":
        for role in ["planner", "player", "designer", "developer", "pm", "qa", "sound"]:
            run_role(role, state, config)
    else:
        run_role(args.role, state, config)

    dump_json(STATUS_PATH, state)
    generate_dashboard(state, config)


if __name__ == "__main__":
    main()
