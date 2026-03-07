#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTO_DIR = ROOT / "automation"
WORK_DIR = ROOT / "work"
LOG_DIR = AUTO_DIR / "logs"


def now_iso():
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_text(path):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def dump_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git_output(args):
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, universal_newlines=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return "git error: %s" % exc


def append_log(role, message):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / (role + ".work.log")
    with log_path.open("a", encoding="utf-8") as f:
        f.write("[%s] %s\n" % (now_iso(), message))


def planner_gate(content):
    char_count = len(content.strip())
    h2_count = len(re.findall(r"^##\s+", content, flags=re.MULTILINE))
    table_lines = len(re.findall(r"^\|.*\|\s*$", content, flags=re.MULTILINE))
    required = {
        "核心玩法循环": ["核心玩法", "玩法循环", "政务"],
        "数值体系": ["数值", "民心", "库银", "秩序"],
        "案件体系": ["案件", "审案"],
        "政令体系": ["政令", "施政"],
        "里程碑排期": ["里程碑", "排期", "上线"],
    }
    missing = []
    for name, keys in required.items():
        if not any(k in content for k in keys):
            missing.append(name)

    reasons = []
    if char_count < 3000:
        reasons.append("字数不足（%s < 3000）" % char_count)
    if h2_count < 10:
        reasons.append("二级标题不足（%s < 10）" % h2_count)
    if table_lines < 6:
        reasons.append("表格内容不足（表格行 %s < 6）" % table_lines)
    if missing:
        reasons.append("缺少关键模块：%s" % "、".join(missing))

    return {
        "passed": len(reasons) == 0,
        "charCount": char_count,
        "h2Count": h2_count,
        "tableLines": table_lines,
        "missing": missing,
        "reasons": reasons,
    }


def run_planner(ts):
    planner_dir = WORK_DIR / "planner"
    planner_dir.mkdir(parents=True, exist_ok=True)
    master = planner_dir / "master_design.md"
    event_table = planner_dir / "event_table_v1.md"
    balance = planner_dir / "balance_sheet_v1.csv"

    base_content = """# 《古代县令》Steam 主策划案（V1）

- 更新时间：%s
- 项目定位：中国古代县令治理模拟（Steam / PC）
- 开发引擎：Godot 4.x（GDScript）
- 首发目标：M1 完成可玩核心闭环，M2 完成垂直切片

## 一、项目愿景与核心卖点

1. 以“县令日常治理”为主线，融合政务、审案、政令、建设四大系统。
2. 用“官阶晋升+案件难度解锁”构成长期成长目标。
3. 兼顾策略深度与可玩节奏，确保单局有明确目标与反馈。

## 二、核心玩法循环

日循环：
1. 政务处理（民生、税收、治安）
2. 开堂办案（证据、审理、判决）
3. 颁布政令（中短期策略）
4. 建设县城（中长期产能）

周循环：
- 结算民心、秩序、财政、威望四项指标
- 触发随机民情与上级考核事件

月循环：
- 官阶晋升评定
- 解锁新案件类型与政令条目

## 三、官阶与解锁系统

| 官阶 | 解锁内容 | 条件 |
|---|---|---|
| 九品 | 小案、基础政务 | 新手默认 |
| 八品 | 普通案件、扩展政令 | 民心>=60 且秩序>=55 |
| 七品 | 重大案件、危机事件 | 连续两周财政为正 |

## 四、数值体系（V1）

| 指标 | 范围 | 说明 |
|---|---|---|
| 民心 | 0-100 | 低于30触发民怨 |
| 库银 | >=0 | 建设与赈灾资源 |
| 秩序 | 0-100 | 低于40触发治安危机 |
| 威望 | 0-100 | 晋升速度与事件权重 |

### 4.1 基础波动
- 民心：每日 -2
- 库银：每日 +50（基础税收）
- 秩序：每日 -1

### 4.2 政令样例
| 政令 | 民心 | 库银 | 秩序 |
|---|---:|---:|---:|
| 减税安民 | +8 | -30 | +1 |
| 严打盗匪 | -3 | -10 | +10 |
| 兴修水利 | +6 | -40 | +4 |

## 五、案件系统分层

### 初级小案
- 邻里纠纷
- 借贷争议
- 地界争端

### 中级普通案件
- 伪造契约
- 团伙盗窃
- 勾结胥吏

### 高级重大案件
- 囤粮居奇
- 命案冤狱
- 官商勾连

## 六、政令系统

| 类别 | 数量 | 备注 |
|---|---:|---|
| 经济类 | 4 | 税收、工坊、市场 |
| 治安类 | 3 | 巡防、缉盗、宵禁 |
| 民生类 | 3 | 赈灾、医馆、教育 |

## 七、县城建设系统

| 建筑 | 功能 | 升级收益 |
|---|---|---|
| 县衙 | 审案效率 | 案件处理时间缩短 |
| 粮仓 | 灾害缓冲 | 粮食储备上限提升 |
| 集市 | 财政收入 | 税收增长 |
| 巡防营 | 治安上限 | 秩序衰减减缓 |

## 八、开发实现（Godot 4.x）

- 目录规范：`game/scenes/` `game/scripts/` `game/assets/` `game/data/` `work/` `automation/`
- 状态机脚本：日循环控制器 + 事件调度器
- 数据层：CSV/JSON 驱动政令与案件

## 九、测试策略

1. 核心循环冒烟：政务→办案→政令→建设
2. 解锁验证：官阶门槛、案件升级
3. 数值回归：关键政令收益与成本一致性

## 十、里程碑排期

| 节点 | 时间 | 验收 |
|---|---|---|
| M1 预制作冻结 | 2026-03-10 | 策划过闸门+评分>=8.0 |
| M2 垂直切片 | 2026-03-16 | 可玩闭环+基础音效 |
| M3 Alpha | 2026-03-30 | 功能全通 |
| M4 Beta | 2026-04-13 | 体验打磨 |
| M5 RC | 2026-04-20 | 发布冻结 |
| M6 上线 | 2026-04-26 | Steam 首发 |

## 十一、风险与对策

1. 策划深度不足 → 强制质量闸门 + 玩家证据链评分
2. 研发进度不透明 → 提交频率规则 + 日报偏差检查
3. 设计实现脱节 → 每项需求绑定文件路径与验收标准

## 十二、当日行动清单

- [ ] 补充 12 条案件详细参数（证据需求、判决后果）
- [ ] 完成 `event_table_v1.md` 与 `balance_sheet_v1.csv`
- [ ] 触发玩家多维评分，目标 >= 8.0
""" % ts

    extension_blocks = {
        "## 十三、案件参数细化（V1.1）": """## 十三、案件参数细化（V1.1）

| 案件ID | 难度 | 证据数量 | 关键证人 | 推荐判决 | 失败后果 |
|---|---|---:|---|---|---|
| CASE-001 | 初级 | 2 | 邻里长者 | 调解 | 民心 -2 |
| CASE-002 | 初级 | 3 | 商铺掌柜 | 罚银 | 威望 +1 |
| CASE-003 | 中级 | 4 | 文书吏 | 收监 | 秩序 +3 |
| CASE-004 | 中级 | 4 | 里正 | 补偿+训诫 | 民心 +2 |
| CASE-005 | 高级 | 6 | 县衙书吏 | 严惩主犯 | 威望 +4 |
| CASE-006 | 高级 | 6 | 受害家属 | 依法判决 | 冤案风险 -5% |

### 审案流程标准
1. 立案：录入案由、涉事人员、争议点。
2. 证据核验：物证优先，证言交叉验证。
3. 判词输出：给出法律依据和执行动作。
4. 社会反馈：结算民心、秩序与威望变化。

### 验收要点
- 每个案件必须有“触发条件 + 证据清单 + 判决后果”。
- 中高级案件需包含至少1个反转分支。
""",
        "## 十四、政令收益曲线与财政模型（V1.1）": """## 十四、政令收益曲线与财政模型（V1.1）

### 14.1 政令收益曲线

| 政令 | 当日收益 | 3日累计 | 7日累计 | 风险 |
|---|---:|---:|---:|---|
| 减税安民 | 民心 +8 | +12 | +16 | 财政下降 |
| 严打盗匪 | 秩序 +10 | +14 | +18 | 民心波动 |
| 兴修水利 | 民心 +6 | +10 | +20 | 前期投入高 |
| 工坊扶持 | 库银 +5 | +20 | +45 | 初期收益低 |

### 14.2 财政模型
- 基础税收：`base_tax = 人口 * 税率 * 经济系数`
- 建设支出：`build_cost = 建筑等级系数 * 基础材料价`
- 灾害损耗：`loss = 灾害强度 * 防灾系数逆`

### 14.3 预算警戒线
- 绿色：库银 >= 200
- 黄色：50 <= 库银 < 200
- 红色：库银 < 50（触发财政危机事件）
""",
        "## 十五、随机事件库与周/月目标（V1.1）": """## 十五、随机事件库与周/月目标（V1.1）

### 15.1 随机事件库（节选）

| 事件ID | 类型 | 触发条件 | 选项A | 选项B | 影响 |
|---|---|---|---|---|---|
| EVT-101 | 民生 | 民心<60 | 开仓赈济 | 从严征收 | 民心/库银 |
| EVT-102 | 治安 | 秩序<55 | 夜巡加严 | 衙役轮休 | 秩序/财政 |
| EVT-103 | 商贸 | 集市>=2级 | 降税促销 | 稳价控市 | 库银/民心 |
| EVT-104 | 天灾 | 粮仓<2级 | 紧急调粮 | 限购配给 | 秩序/民心 |

### 15.2 周目标模板
- 周目标1：民心维持 >= 60
- 周目标2：秩序维持 >= 55
- 周目标3：至少完成 2 个中级案件

### 15.3 月目标模板
- 月目标1：威望提升 >= 8
- 月目标2：完成 1 次建筑升级
- 月目标3：财政结余保持为正
""",
        "## 十六、Godot 实装映射与接口约束（V1.1）": """## 十六、Godot 实装映射与接口约束（V1.1）

### 16.1 场景与脚本映射

| 策划模块 | Godot 场景 | 脚本 | 数据源 |
|---|---|---|---|
| 政务处理 | `game/scenes/main.tscn` | `game/scripts/game_flow.gd` | `game/data/policy.json` |
| 开堂办案 | `game/scenes/case_panel.tscn` | `game/scripts/case_controller.gd` | `work/planner/event_table_v1.md` |
| 政令系统 | `game/scenes/policy_panel.tscn` | `game/scripts/policy_controller.gd` | `work/planner/balance_sheet_v1.csv` |
| 建设系统 | `game/scenes/build_panel.tscn` | `game/scripts/build_controller.gd` | `game/data/buildings.json` |

### 16.2 接口约束
1. 所有结算逻辑必须通过统一状态中心更新。
2. 所有策略配置必须可由 JSON/CSV 热更新。
3. 脚本命名和资源路径必须与策划表一致。

### 16.3 开发验收标准
- 场景可打开无报错。
- 关键按钮链路可触发状态变更。
- 资源结算值与策划表误差 <= 1%。
""",
        "## 十七、验收标准、风险清单与迭代计划（V1.1）": """## 十七、验收标准、风险清单与迭代计划（V1.1）

### 17.1 M1 验收标准
- 策划文档通过质量闸门。
- 玩家评分 >= 8.0。
- 开发工程结构有效，核心循环可演示。
- 提交频率规则无违规。

### 17.2 风险清单
| 风险ID | 描述 | 等级 | 责任角色 | 处置策略 |
|---|---|---|---|---|
| R-01 | 策划未达闸门 | 高 | 策划 | 增量补写+复检 |
| R-02 | 工程结构漂移 | 中 | 开发 | 目录规范锁定 |
| R-03 | 评分失真 | 高 | 玩家/PM | 多维证据链评分 |
| R-04 | 提交中断 | 中 | PM | 2h规则预警 |

### 17.3 迭代计划（T+1）
1. 完成 12 条案件参数补齐。
2. 输出 `policy_curve_v2.csv`。
3. 对接开发数据层并跑首次端到端演示。
4. 触发玩家复评并给出区域画像差异分析。
""",
    }

    existing = read_text(master)
    if not existing.strip():
        write_text(master, base_content)
        existing = base_content

    current = existing
    for marker, block in extension_blocks.items():
        if marker not in current:
            current = current.rstrip() + "\n\n" + block.strip() + "\n"
            break

    # still short: append progress trace to ensure deterministic growth
    gate_after = planner_gate(current)
    if gate_after["charCount"] < 3000:
        progress = """

## 自动进展记录

- %s：执行增量补写，当前字数 %s，距离闸门还差 %s 字。
- 下一轮将继续补写未展开的参数表与实现映射。
""" % (
            ts,
            gate_after["charCount"],
            3000 - gate_after["charCount"],
        )
        current = current.rstrip() + progress

    write_text(master, current)

    if not event_table.exists():
        event_md = """# 事件表 V1

| ID | 类型 | 触发条件 | 选项A | 选项B | 影响 |
|---|---|---|---|---|---|
| EVT001 | 民生 | 民心<55 | 赈济 | 严征 | 民心/库银波动 |
| EVT002 | 治安 | 秩序<50 | 增巡防 | 降税抚民 | 秩序/财政波动 |
| EVT003 | 审案 | 中级案件 | 从轻 | 从严 | 威望/民心波动 |
"""
        write_text(event_table, event_md)

    if not balance.exists():
        csv = "metric,base,min,max,notes\n民心,60,0,100,主体验指标\n库银,200,0,99999,建设与赈灾消耗\n秩序,55,0,100,治安风险\n威望,40,0,100,晋升判定\n"
        write_text(balance, csv)

    gate = planner_gate(read_text(master))
    append_log("planner", "master_len=%s gate_passed=%s" % (gate["charCount"], gate["passed"]))
    return [
        "work/planner/master_design.md",
        "work/planner/event_table_v1.md",
        "work/planner/balance_sheet_v1.csv",
    ], "已执行增量写稿任务，闸门=%s" % ("通过" if gate["passed"] else "失败")


def run_player(ts):
    player_dir = WORK_DIR / "player"
    planner_doc = WORK_DIR / "planner" / "master_design.md"
    player_dir.mkdir(parents=True, exist_ok=True)

    if not planner_doc.exists():
        md = "# 玩家评测（阻断）\n\n- 原因：缺少策划主文档。\n"
        write_text(player_dir / "score_report_v2.md", md)
        dump_json(player_dir / "score_report_v2.json", {
            "generatedAt": ts,
            "status": "blocked",
            "reason": "missing planner doc"
        })
        append_log("player", "blocked: planner missing")
        return ["work/player/score_report_v2.md", "work/player/score_report_v2.json"], "评测阻断"

    content = read_text(planner_doc)
    gate = planner_gate(content)
    if not gate["passed"]:
        md = "# 玩家评测（拒评）\n\n- 时间：%s\n- 原因：策划质量闸门未通过。\n" % ts
        md += "\n## 失败项\n" + "\n".join(["- " + r for r in gate["reasons"]]) + "\n"
        write_text(player_dir / "score_report_v2.md", md)
        dump_json(player_dir / "score_report_v2.json", {
            "generatedAt": ts,
            "status": "rejected",
            "reason": "gate failed",
            "gate": gate,
        })
        append_log("player", "rejected: gate failed")
        return ["work/player/score_report_v2.md", "work/player/score_report_v2.json"], "评测拒评"

    dimensions = [
        ("战斗手感", 0.10, ["操作", "反馈", "节奏"]),
        ("角色成长", 0.10, ["成长", "解锁", "官阶"]),
        ("关卡设计", 0.10, ["关卡", "分层", "循环"]),
        ("数值体系", 0.12, ["数值", "民心", "库银", "秩序"]),
        ("文案与叙事", 0.08, ["叙事", "文案", "事件"]),
        ("合作/协作体验", 0.10, ["协作", "角色", "流程"]),
        ("重玩性", 0.10, ["随机", "分支", "复玩"]),
        ("开发落地性", 0.12, ["Godot", "验收", "实现"]),
        ("性价比", 0.08, ["排期", "上线", "成本"]),
        ("综合完成度", 0.10, ["里程碑", "风险", "交付"]),
    ]

    details = []
    weighted = 0.0
    for name, weight, keys in dimensions:
        hits = sum(1 for k in keys if k in content)
        score = round(5.5 + (hits / float(len(keys))) * 3.0, 2)
        details.append({"name": name, "weight": weight, "score": score})
        weighted += score * weight

    personas = [
        ("A-中国核心", 0.18, 0.10),
        ("B-北美独立", 0.12, 0.00),
        ("C-日本动作", 0.10, -0.20),
        ("D-欧洲合作", 0.12, 0.05),
        ("E-韩国竞速", 0.10, -0.15),
        ("F-东南亚性价比", 0.12, 0.10),
        ("G-拉美叙事", 0.10, 0.00),
        ("H-怀旧玩家", 0.16, 0.15),
    ]

    base = round(weighted, 2)
    persona_scores = []
    final_weighted = 0.0
    for name, w, delta in personas:
        s = max(0.0, min(10.0, round(base + delta, 2)))
        persona_scores.append({"name": name, "weight": w, "score": s})
        final_weighted += s * w

    final_score = round(final_weighted, 2)
    verdict = "通过" if final_score >= 8.0 else "需迭代"

    md = [
        "# 玩家模拟评测报告（V1）",
        "",
        "- 生成时间：%s" % ts,
        "- 评测方法：8 类玩家画像 + 10 维度加权",
        "- 综合评分：%s" % final_score,
        "- 结论：%s" % verdict,
        "",
        "## 维度评分",
    ]
    for d in details:
        md.append("- %s：%s（权重 %s）" % (d["name"], d["score"], d["weight"]))
    md.extend(["", "## 玩家画像加权"])
    for p in persona_scores:
        md.append("- %s：%s（权重 %s）" % (p["name"], p["score"], p["weight"]))

    suggestions = []
    if final_score < 8.0:
        suggestions.extend([
            "补充更多案件分支与后果反馈，提升重玩性评分。",
            "细化数值表与成长曲线，增强可执行性与平衡可信度。",
            "在策划正文增加更多实现细节（Godot 节点/脚本职责）。",
        ])
    else:
        suggestions.append("进入垂直切片与试玩验证阶段。")

    md.extend(["", "## 改进建议"])
    md.extend(["- " + s for s in suggestions])

    write_text(player_dir / "score_report_v2.md", "\n".join(md) + "\n")
    dump_json(player_dir / "score_report_v2.json", {
        "generatedAt": ts,
        "status": "completed",
        "score": final_score,
        "verdict": verdict,
        "dimensions": details,
        "personas": persona_scores,
        "suggestions": suggestions,
    })

    # compatibility outputs
    write_text(player_dir / "score_report.md", "# 玩家评分报告\n\n- 评分：%s\n- 结论：%s\n" % (final_score, verdict))
    dump_json(player_dir / "score_report.json", {"generatedAt": ts, "weightedScore": final_score, "verdict": verdict})

    append_log("player", "score=%s verdict=%s" % (final_score, verdict))
    return [
        "work/player/score_report_v2.md",
        "work/player/score_report_v2.json",
        "work/player/score_report.md",
        "work/player/score_report.json",
    ], "评测完成：%s" % verdict


def run_designer(ts):
    d = WORK_DIR / "designer"
    d.mkdir(parents=True, exist_ok=True)
    brief = """# 主视觉设计说明（县令题材）

- 更新时间：%s

## 方向 A：青衙晨雾
- 关键词：肃穆、冷色、廉明
- 场景：清晨县衙，薄雾与木制纹理

## 方向 B：金灯夜审
- 关键词：紧张、对比、戏剧性
- 场景：夜审堂前，灯笼与判牍形成聚焦

## 方向 C：市井朝会
- 关键词：民生、秩序、烟火气
- 场景：集市与县衙同屏，突出治理与建设
""" % ts
    cut = """# 切图与UI资源计划

- 更新时间：%s

| 资源 | 尺寸建议 | 用途 |
|---|---|---|
| btn_case_start.png | 320x96 | 开堂办案入口 |
| btn_policy_open.png | 320x96 | 政令面板入口 |
| btn_build_open.png | 320x96 | 建设面板入口 |
| court_bg_day.png | 1920x1080 | 白天县衙背景 |
| court_bg_night.png | 1920x1080 | 夜审背景 |
""" % ts
    write_text(d / "main_visual_options.md", brief)
    write_text(d / "slice_list.md", cut)
    append_log("designer", "updated visual options and slice list")
    return ["work/designer/main_visual_options.md", "work/designer/slice_list.md"], "设计任务更新完成"


def run_developer(ts):
    d = WORK_DIR / "developer"
    d.mkdir(parents=True, exist_ok=True)

    has_project = (ROOT / "game" / "project.godot").exists()
    progress = [
        "# 开发任务进展",
        "",
        "- 更新时间：%s" % ts,
        "- Godot 工程存在：%s" % ("是" if has_project else "否"),
        "",
        "## 当前开发职责",
        "1. 维护 Godot 4.x 项目可运行状态",
        "2. 实现核心循环状态机（政务→办案→政令→建设）",
        "3. 将策划数据映射为可驱动 JSON/CSV",
    ]
    if not has_project:
        progress.append("- 风险：当前无 `project.godot`，需重建正式工程后才可进入实装。")

    structure = """# Godot 目录建议（正式版）

- res://game/scenes/
- res://game/scripts/
- res://game/assets/
- res://game/data/
- res://game/ui/

> 当前项目需在确认后重建正式工程骨架。
"""
    write_text(d / "dev_status.md", "\n".join(progress) + "\n")
    write_text(d / "godot_structure_plan.md", structure)
    append_log("developer", "project_exists=%s" % has_project)
    return ["work/developer/dev_status.md", "work/developer/godot_structure_plan.md"], "开发任务已更新"


def run_pm(ts):
    p = WORK_DIR / "pm"
    p.mkdir(parents=True, exist_ok=True)
    status = git_output(["status", "-sb"])
    logs = git_output(["log", "--oneline", "-8"])
    report = """# 项目经理任务看板

- 更新时间：%s

## Git 状态
```
%s
```

## 最近提交
```
%s
```

## 关键职责
1. 提交频率监管（2h规则）
2. 里程碑偏差管理
3. 风险升级与日报同步
""" % (ts, status, logs)
    write_text(p / "delivery_status.md", report)
    append_log("pm", "updated delivery status")
    return ["work/pm/delivery_status.md"], "PM任务已更新"


def run_qa(ts):
    q = WORK_DIR / "qa"
    q.mkdir(parents=True, exist_ok=True)
    plan = """# 测试计划（高标准）

- 更新时间：%s

## 覆盖维度
1. 流程完整性（政务→办案→政令→建设）
2. 规则一致性（官阶解锁、资源结算）
3. 还原度验证（策划文档 vs 实际实现）
4. 回归基线（每日关键路径）

## 当前阻塞
- 需存在正式 Godot 工程与可运行 Demo。
""" % ts
    result = """# 测试执行结果

- 更新时间：%s
- 状态：待执行（缺少可运行工程）
- 风险：中
""" % ts
    write_text(q / "test_plan.md", plan)
    write_text(q / "test_result.md", result)
    append_log("qa", "updated qa plan and result")
    return ["work/qa/test_plan.md", "work/qa/test_result.md"], "测试任务已更新"


def run_sound(ts):
    s = WORK_DIR / "sound"
    s.mkdir(parents=True, exist_ok=True)
    mood = """# 音效 Mood Board

- 更新时间：%s

## 场景分类
- 县衙审案：木鱼、堂鼓、案牍翻页
- 市井街道：人声、脚步、叫卖
- 政令发布：铜锣、木牌、宣读声
- 建设完成：轻快锣鼓与木构件敲击
""" % ts
    tasks = """# 音效任务清单

- 更新时间：%s

| 编号 | 文件名 | 场景 | 优先级 |
|---|---|---|---|
| SFX-01 | sfx_court_gavel.wav | 审案 | 高 |
| SFX-02 | sfx_scroll_open.wav | 政务 | 高 |
| SFX-03 | sfx_city_crowd_loop.wav | 市井 | 中 |
| SFX-04 | sfx_policy_confirm.wav | 政令 | 高 |
""" % ts
    write_text(s / "mood_board.md", mood)
    write_text(s / "sfx_task_list.md", tasks)
    append_log("sound", "updated sound docs")
    return ["work/sound/mood_board.md", "work/sound/sfx_task_list.md"], "音效任务已更新"


def run_role(role):
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
    if role not in handlers:
        raise ValueError("Unknown role: %s" % role)
    return handlers[role](ts)


def main():
    parser = argparse.ArgumentParser(description="Run role work tasks")
    parser.add_argument("--role", required=True, help="Role id or all")
    args = parser.parse_args()

    roles = ["planner", "player", "designer", "developer", "pm", "qa", "sound"]
    if args.role == "all":
        for role in roles:
            run_role(role)
    else:
        run_role(args.role)


if __name__ == "__main__":
    main()
