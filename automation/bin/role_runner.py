#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTO_DIR = ROOT / "automation"
CONFIG_PATH = AUTO_DIR / "configs" / "roles.json"
STATUS_PATH = AUTO_DIR / "state" / "status.json"
DASHBOARD_PATH = AUTO_DIR / "reports" / "dashboard.md"

MASTER_DESIGN_PATH = ROOT / "work" / "planner" / "master_design.md"
DESIGN_STATUS_PATH = AUTO_DIR / "checks" / "planner" / "design_status.md"
GATE_JSON_PATH = AUTO_DIR / "checks" / "planner" / "gate_check.json"
GATE_MD_PATH = AUTO_DIR / "checks" / "planner" / "gate_check.md"

SCORE_V2_JSON_PATH = ROOT / "work" / "player" / "score_report_v2.json"
SCORE_V2_MD_PATH = ROOT / "work" / "player" / "score_report_v2.md"
LEGACY_SCORE_JSON_PATH = ROOT / "work" / "player" / "score_report.json"
LEGACY_SCORE_MD_PATH = ROOT / "work" / "player" / "score_report.md"


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
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, universal_newlines=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception as exc:
        return f"git error: {exc}"


def check_godot_project() -> dict:
    project_file = ROOT / "game" / "project.godot"
    scenes = sorted(str(path.relative_to(ROOT)) for path in ROOT.rglob("*.tscn"))
    scripts = sorted(str(path.relative_to(ROOT)) for path in ROOT.rglob("*.gd"))
    return {
        "projectExists": project_file.exists(),
        "projectPath": "game/project.godot" if project_file.exists() else None,
        "sceneCount": len(scenes),
        "scriptCount": len(scripts),
        "sampleScenes": scenes[:10],
        "sampleScripts": scripts[:10],
    }


def evaluate_planner_gate(content: str) -> dict:
    char_count = len(content.strip())
    section_h2_count = len(re.findall(r"^##\s+", content, flags=re.MULTILINE))
    table_line_count = len(re.findall(r"^\|.*\|\s*$", content, flags=re.MULTILINE))

    required_blocks = {
        "核心玩法循环": ["核心玩法", "玩法循环", "循环"],
        "数值体系": ["数值", "公式", "资源", "平衡"],
        "案件体系": ["案件", "审案", "判决"],
        "政令体系": ["政令", "法令", "施政"],
    }

    missing_blocks = []
    for block_name, keywords in required_blocks.items():
        if not any(keyword in content for keyword in keywords):
            missing_blocks.append(block_name)

    reasons = []
    if char_count < 3000:
        reasons.append(f"字数不足（{char_count} < 3000）")
    if section_h2_count < 10:
        reasons.append(f"二级标题不足（{section_h2_count} < 10）")
    if table_line_count < 6:
        reasons.append(f"表格内容不足（表格行 {table_line_count} < 6）")
    if missing_blocks:
        reasons.append("缺少关键模块：" + "、".join(missing_blocks))

    return {
        "passed": len(reasons) == 0,
        "charCount": char_count,
        "sectionH2Count": section_h2_count,
        "tableLineCount": table_line_count,
        "missingBlocks": missing_blocks,
        "reasons": reasons,
    }


def extract_evidence_lines(content: str, keywords, limit: int = 2):
    evidence = []
    seen = set()
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if any(keyword in line for keyword in keywords):
            if line not in seen:
                seen.add(line)
                evidence.append(line[:120])
        if len(evidence) >= limit:
            break
    if not evidence:
        return ["未找到直接证据，请补充对应章节内容。"]
    return evidence


def score_dimension(content: str, keywords):
    matched = [keyword for keyword in keywords if keyword in content]
    coverage = len(matched) / len(keywords) if keywords else 0
    score = round(4.0 + 6.0 * coverage, 2)
    if not matched:
        score = 3.0
    return score, matched


def run_planner(ts: str):
    initialized = False
    if not MASTER_DESIGN_PATH.exists():
        seed = """# 《古代县令》主策划案（待完善）\n\n> 说明：本文件为正式策划案，禁止自动模板覆盖，仅允许人工或增量修订。\n\n## 当前状态\n\n- 正式策划文件已初始化。\n- 请补充完整内容后再触发玩家评审。\n"""
        write_text(MASTER_DESIGN_PATH, seed)
        initialized = True

    master_content = read_text(MASTER_DESIGN_PATH)
    gate_result = evaluate_planner_gate(master_content)
    gate_result["checkedAt"] = ts
    dump_json(GATE_JSON_PATH, gate_result)

    gate_md = [
        "# 策划质量闸门检查",
        "",
        f"- 检查时间：{ts}",
        f"- 闸门结果：{'通过' if gate_result['passed'] else '失败'}",
        f"- 字数：{gate_result['charCount']}",
        f"- 二级标题数：{gate_result['sectionH2Count']}",
        f"- 表格行数：{gate_result['tableLineCount']}",
    ]
    if gate_result["missingBlocks"]:
        gate_md.append("- 缺失模块：" + "、".join(gate_result["missingBlocks"]))
    gate_md.append("")
    gate_md.append("## 失败原因")
    if gate_result["reasons"]:
        gate_md.extend([f"- {reason}" for reason in gate_result["reasons"]])
    else:
        gate_md.append("- 无")
    write_text(GATE_MD_PATH, "\n".join(gate_md) + "\n")

    status_md = [
        "# 策划状态巡检",
        "",
        f"- 更新时间：{ts}",
        f"- 正式策划文件：`{MASTER_DESIGN_PATH.relative_to(ROOT)}`",
        f"- 自动覆盖保护：开启（本次{'初始化' if initialized else '未覆盖'}正式策划文件）",
        f"- 质量闸门：{'通过' if gate_result['passed'] else '失败'}",
        f"- 当前字数：{gate_result['charCount']}",
        "",
        "## 下一步",
    ]
    if gate_result["passed"]:
        status_md.append("- 已满足评分前置条件，可进入玩家多维评审。")
    else:
        status_md.append("- 请先补足策划内容，再触发玩家评审。")
        status_md.extend([f"- 待修复：{reason}" for reason in gate_result["reasons"]])
    write_text(DESIGN_STATUS_PATH, "\n".join(status_md) + "\n")

    notes = "正式策划通过质量闸门，可进入真实评审" if gate_result["passed"] else "正式策划未通过质量闸门，已阻断评分"
    return [
        str(MASTER_DESIGN_PATH.relative_to(ROOT)),
        str(DESIGN_STATUS_PATH.relative_to(ROOT)),
        str(GATE_MD_PATH.relative_to(ROOT)),
        str(GATE_JSON_PATH.relative_to(ROOT)),
    ], notes


def run_player(ts: str):
    """Inspect existing player AI evaluation artifacts only.

    Important: this checker must not overwrite `work/player/*` scoring outputs.
    """
    audit_dir = AUTO_DIR / "checks" / "player"
    audit_json_path = audit_dir / "score_audit.json"
    audit_md_path = audit_dir / "score_audit.md"

    gate_result = {
        "passed": False,
        "reasons": ["缺少正式策划文件"],
    }
    if MASTER_DESIGN_PATH.exists():
        content = read_text(MASTER_DESIGN_PATH)
        gate_result = evaluate_planner_gate(content)
        gate_result["checkedAt"] = ts
    dump_json(GATE_JSON_PATH, gate_result)

    score_report = {}
    score_md = read_text(SCORE_V2_MD_PATH)
    if SCORE_V2_JSON_PATH.exists():
        try:
            score_report = load_json(SCORE_V2_JSON_PATH)
        except Exception as exc:
            score_report = {"parseError": str(exc)}

    weighted_score = score_report.get("weightedScore")
    if weighted_score is None:
        weighted_score = (score_report.get("compositeScore") or {}).get("overall")
    verdict = score_report.get("verdict")
    if verdict is None:
        verdict = (score_report.get("compositeScore") or {}).get("verdict")
    has_ai_evidence = "证据链" in score_md or "画像" in score_md

    status = "blocked"
    findings = []
    suggestions = []

    if not MASTER_DESIGN_PATH.exists():
        findings.append("缺少正式策划文件，玩家评测前置条件不满足")
        suggestions.append("先补齐 work/planner/master_design.md")
    elif not gate_result.get("passed"):
        findings.append("策划质量闸门未通过，玩家评分应拒评")
        reasons = gate_result.get("reasons") or []
        findings.extend([f"闸门失败：{r}" for r in reasons])
        suggestions.append("先修复闸门失败项，再触发 AI 玩家评测")
    else:
        status = "ok"
        if not SCORE_V2_JSON_PATH.exists() or not SCORE_V2_MD_PATH.exists():
            status = "invalid"
            findings.append("缺少玩家评测产物（score_report_v2.json 或 .md）")
            suggestions.append("触发玩家 AI 任务生成最新评测")
        else:
            if not isinstance(weighted_score, (int, float)):
                status = "invalid"
                findings.append("score_report_v2.json 缺少有效 weightedScore")
            allowed_verdicts = ["通过", "需迭代", "拒评", "良好，具备上线潜力，建议微调后发布"]
            if verdict not in allowed_verdicts:
                status = "invalid"
                findings.append("score_report_v2.json verdict 字段无效")
            if not has_ai_evidence:
                status = "warning" if status == "ok" else status
                findings.append("score_report_v2.md 缺少明确 AI 证据链描述")
                suggestions.append("在评测报告中补充画像/维度证据链")

    if status == "ok" and not suggestions:
        suggestions.append("玩家评测产物结构有效，继续沿用 AI 评分流程")

    audit = {
        "checkedAt": ts,
        "status": status,
        "gate": {
            "passed": gate_result.get("passed", False),
            "reasons": gate_result.get("reasons", []),
        },
        "score": {
            "weightedScore": weighted_score,
            "verdict": verdict,
            "reportJson": str(SCORE_V2_JSON_PATH.relative_to(ROOT)),
            "reportMd": str(SCORE_V2_MD_PATH.relative_to(ROOT)),
        },
        "findings": findings,
        "suggestions": suggestions,
        "mode": "inspection_only_no_recompute",
    }
    dump_json(audit_json_path, audit)

    md_lines = [
        "# 玩家评测审计（仅校验，不重算）",
        "",
        f"- 检查时间：{ts}",
        f"- 审计状态：{status}",
        f"- 策划闸门：{'通过' if gate_result.get('passed') else '失败'}",
        f"- 当前评分：{weighted_score if weighted_score is not None else '未知'}（{verdict or '未知'}）",
        "",
        "## 发现",
    ]
    if findings:
        md_lines.extend([f"- {item}" for item in findings])
    else:
        md_lines.append("- 无")

    md_lines.extend(["", "## 建议"])
    md_lines.extend([f"- {item}" for item in suggestions])
    write_text(audit_md_path, "\n".join(md_lines) + "\n")

    artifacts = [
        str(audit_json_path.relative_to(ROOT)),
        str(audit_md_path.relative_to(ROOT)),
    ]
    if SCORE_V2_JSON_PATH.exists():
        artifacts.append(str(SCORE_V2_JSON_PATH.relative_to(ROOT)))
    if SCORE_V2_MD_PATH.exists():
        artifacts.append(str(SCORE_V2_MD_PATH.relative_to(ROOT)))

    return artifacts, "已校验 AI 玩家评测产物（未进行脚本重算）"


def run_designer(ts: str):
    options = f"""# 主视觉方案（自动任务）\n\n更新时间：{ts}\n\n1. **青衙晨雾版**：冷色主调，强调肃穆断案气质。\n2. **金灯夜审版**：暖色高对比，突出夜审紧张氛围。\n3. **市井朝会版**：中性色，突出县城建设与民生。\n"""
    slices = f"""# 切图清单（自动任务）\n\n更新时间：{ts}\n\n- UI/btn_case_start.png\n- UI/btn_policy_open.png\n- UI/btn_build_open.png\n- Scene/court_bg_day.png\n- Scene/court_bg_night.png\n"""
    out1 = ROOT / "work" / "designer" / "main_visual_options.md"
    out2 = ROOT / "work" / "designer" / "slice_list.md"
    write_text(out1, options)
    write_text(out2, slices)
    return [str(out1.relative_to(ROOT)), str(out2.relative_to(ROOT))], "已更新主视觉与切图清单"


def run_developer(ts: str):
    check = check_godot_project()
    out_json = AUTO_DIR / "checks" / "developer" / "godot_project_check.json"
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
    out_md = ROOT / "work" / "developer" / "dev_status.md"
    write_text(out_md, "\n".join(status) + "\n")
    notes = "Godot 工程已检测" if check["projectExists"] else "Godot 工程缺失，需立即创建"
    return [str(out_md.relative_to(ROOT)), str(out_json.relative_to(ROOT))], notes




def analyze_commit_frequency(ts: str) -> dict:
    count_24h_raw = git_output(["rev-list", "--count", "--since=24 hours ago", "HEAD"])
    try:
        commits_24h = int(count_24h_raw)
    except Exception:
        commits_24h = 0

    last_commit_iso = git_output(["log", "-1", "--format=%cI"])
    minutes_since = None
    if last_commit_iso and not last_commit_iso.startswith("git error"):
        try:
            last_unix_raw = git_output(["log", "-1", "--format=%ct"])
            last_unix = int(last_unix_raw)
            import time
            now_unix = int(time.time())
            minutes_since = int((now_unix - last_unix) // 60)
        except Exception:
            minutes_since = None

    status = "正常"
    if minutes_since is not None and minutes_since > 240:
        status = "高风险"
    elif minutes_since is not None and minutes_since > 120:
        status = "警告"

    violated_2h = minutes_since is not None and minutes_since > 120
    violated_4h = minutes_since is not None and minutes_since > 240

    return {
        "checkedAt": ts,
        "commitsLast24h": commits_24h,
        "lastCommitIso": last_commit_iso,
        "minutesSinceLastCommit": minutes_since,
        "violated2hRule": violated_2h,
        "violated4hRule": violated_4h,
        "status": status,
        "policyPath": "work/pm/git_commit_policy.md",
    }


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

    schedule_path = ROOT / "work" / "pm" / "project_schedule.md"
    schedule_exists = schedule_path.exists()
    planner_content = read_text(MASTER_DESIGN_PATH)
    milestone_declared_by_planner = any(token in planner_content for token in ["里程碑", "排期", "上线"])
    milestone_schedule_by_pm = schedule_exists and len(read_text(schedule_path).strip()) > 0

    gate_result = load_json(GATE_JSON_PATH)
    gate_passed = gate_result.get("passed") is True

    player_report = load_json(SCORE_V2_JSON_PATH)
    player_score = player_report.get("weightedScore")
    if player_score is None:
        player_score = (player_report.get("compositeScore") or {}).get("overall")
    player_verdict = player_report.get("verdict")
    if player_verdict is None:
        player_verdict = (player_report.get("compositeScore") or {}).get("verdict", "未知")

    commit_freq = analyze_commit_frequency(ts)

    risk = [
        "# 项目风险日志",
        "",
        f"- 更新时间：{ts}",
    ]
    if "No commits yet" in log_short or "does not have any commits yet" in log_short:
        risk.append("- 风险：仓库尚无提交，18:00 日报无法提供版本里程碑。")
    if "game/project.godot" not in read_text(AUTO_DIR / "checks" / "developer" / "godot_project_check.json"):
        risk.append("- 风险：开发工程状态未知或未检测。")
    if not milestone_declared_by_planner:
        risk.append("- 风险：策划未声明里程碑目标（需在 master_design.md 给出里程碑定义）。")
    if not milestone_schedule_by_pm:
        risk.append("- 风险：项目经理未提供里程碑排期（需维护 work/pm/project_schedule.md）。")
    if not gate_passed:
        reasons = gate_result.get("reasons") or ["策划质量闸门未通过"]
        for reason in reasons:
            risk.append(f"- 风险：质量闸门失败 - {reason}")
    if isinstance(player_score, (int, float)) and player_score < 8.0:
        risk.append(f"- 风险：玩家评分 {player_score} < 8.0，未达到 M1 门槛。")
    if player_verdict == "拒评":
        risk.append("- 风险：玩家评审被拒绝，当前评分无效。")
    if commit_freq.get("violated2hRule"):
        risk.append(f"- 风险：提交频率违规（距上次提交 {commit_freq.get('minutesSinceLastCommit')} 分钟 > 120 分钟）。")
    if commit_freq.get("violated4hRule"):
        risk.append("- 风险升级：提交中断超过 4 小时。")

    out_risk = ROOT / "work" / "pm" / "risk_log.md"
    write_text(out_risk, "\n".join(risk) + "\n")

    daily = [
        "# 项目经理日报（自动生成）",
        "",
        f"- 生成时间：{ts}",
        f"- 策划里程碑声明：{'已声明' if milestone_declared_by_planner else '缺失'}",
        f"- PM排期文件：{'已加载' if milestone_schedule_by_pm else '缺失'}",
        f"- 质量闸门：{'通过' if gate_passed else '失败'}",
        f"- 玩家评分：{player_score if player_score is not None else '未知'}（{player_verdict}）",
        "",
        "## 里程碑偏差检查",
        "- 责任分工：策划负责里程碑目标声明；项目经理负责里程碑排期维护",
        f"- 目标声明状态：{'已就绪' if milestone_declared_by_planner else '缺失'}（work/planner/master_design.md）",
        f"- 排期维护状态：{'已就绪' if milestone_schedule_by_pm else '缺失'}（work/pm/project_schedule.md）",
        f"- 偏差结论：{'存在偏差（评分未达标/拒评或里程碑治理缺失）' if (player_verdict == '拒评' or (isinstance(player_score, (int, float)) and player_score < 8.0) or (not milestone_declared_by_planner) or (not milestone_schedule_by_pm)) else '暂无明显偏差'}",
        "",
        "## 质量证据链",
        f"- 策划闸门：`{GATE_MD_PATH.relative_to(ROOT)}`",
        f"- 玩家评审：`{SCORE_V2_MD_PATH.relative_to(ROOT)}`",
        "",
        "## 提交频率检查",
        f"- 最近24h提交次数：{commit_freq.get('commitsLast24h')}",
        f"- 距上次提交（分钟）：{commit_freq.get('minutesSinceLastCommit')}",
        f"- 频率状态：{commit_freq.get('status')}",
        f"- 规则文档：`{commit_freq.get('policyPath')}`",
        "",
        "## Git 节点",
        "```",
        log_short,
        "```",
        "",
        "## 今日动作",
        "- 已更新风险日志与提交活动记录",
        "- 已按质量闸门 + 真实评审机制进行偏差检查",
        "",
    ]
    out_daily = AUTO_DIR / "reports" / "daily_report.md"
    write_text(out_daily, "\n".join(daily) + "\n")

    freq_json_path = ROOT / "work" / "pm" / "commit_frequency_check.json"
    dump_json(freq_json_path, commit_freq)

    return [
        str(out_report.relative_to(ROOT)),
        str(out_risk.relative_to(ROOT)),
        str(out_daily.relative_to(ROOT)),
        str(freq_json_path.relative_to(ROOT)),
    ], "已更新 Git 活动、风险日志、日报与提交频率检查"


def run_qa(ts: str):
    plan = f"""# 测试计划（自动任务）\n\n- 更新时间：{ts}\n- 覆盖流程：政务处理、开堂办案、政令发布、县城建设\n- 覆盖维度：功能正确性、解锁条件、数据一致性、还原度\n\n## 待测前置\n- 需存在 Godot 可运行工程与最小 demo。\n- 需策划质量闸门通过后再进入玩法一致性验证。\n"""
    result = f"""# 测试结果（自动巡检）\n\n- 更新时间：{ts}\n- 当前结论：未执行自动化用例（缺少可执行 demo 或正式测试场景）。\n- 风险级别：中\n"""
    out1 = ROOT / "work" / "qa" / "test_plan.md"
    out2 = ROOT / "work" / "qa" / "test_result.md"
    write_text(out1, plan)
    write_text(out2, result)
    return [str(out1.relative_to(ROOT)), str(out2.relative_to(ROOT))], "测试计划已更新，等待 demo"


def run_sound(ts: str):
    mood = f"""# 音效 Mood Board（自动任务）\n\n- 更新时间：{ts}\n\n## 场景氛围\n- 衙门审案：木鱼、堂鼓、低频环境底噪\n- 县城街市：人声远景、叫卖、脚步\n- 政令发布：铜锣、卷轴展开、木牌敲击\n"""
    task = f"""# 音效任务清单\n\n- 更新时间：{ts}\n- sfx_court_gavel.wav\n- sfx_scroll_open.wav\n- sfx_city_crowd_loop.wav\n- sfx_policy_confirm.wav\n"""
    out1 = ROOT / "work" / "sound" / "mood_board.md"
    out2 = ROOT / "work" / "sound" / "sfx_task_list.md"
    write_text(out1, mood)
    write_text(out2, task)
    return [str(out1.relative_to(ROOT)), str(out2.relative_to(ROOT))], "音效 mood board 已更新"


def generate_dashboard(state: dict, config: dict):
    gate_result = load_json(GATE_JSON_PATH)
    player_report = load_json(SCORE_V2_JSON_PATH)
    player_score = player_report.get('weightedScore')
    if player_score is None:
        player_score = (player_report.get('compositeScore') or {}).get('overall', '未知')
    player_verdict = player_report.get('verdict')
    if player_verdict is None:
        player_verdict = (player_report.get('compositeScore') or {}).get('verdict', '未评审')

    lines = [
        "# 角色后台监控面板",
        "",
        f"- 项目：{config.get('project', '')}",
        f"- 最近刷新：{state.get('lastRunAt')}",
        f"- 策划质量闸门：{'通过' if gate_result.get('passed') else '失败/未检查'}",
        f"- 玩家最新评分：{player_score}（{player_verdict}）",
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
        "- 正式策划文件禁止模板覆盖，只允许增量修订。",
        "- 策划质量闸门不通过时，玩家评分必须拒评。",
        "- 里程碑治理分工：策划定义目标，项目经理维护排期。",
        "- 日报必须附质量闸门结果与评分证据链。",
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
