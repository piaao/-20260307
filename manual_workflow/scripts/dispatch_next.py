#!/usr/bin/env python3
import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANUAL = ROOT / 'manual_workflow'
STATE_PATH = MANUAL / 'state' / 'runtime_state.json'
PM_STATUS_PATH = ROOT / 'work' / 'pm' / 'delivery_status.md'
GATE_PATH = ROOT / 'automation' / 'checks' / 'planner' / 'gate_check.json'
PLAYER_SCORE_PATH = ROOT / 'work' / 'player' / 'score_report_v2.json'


def now_str():
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec='seconds')


def load_json(path: Path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def planner_ready():
    planner = ROOT / 'work' / 'planner'
    needed = [
        planner / 'master_design.md',
        planner / 'event_table_v1.md',
        planner / 'balance_sheet_v1.csv',
        planner / 'copy_deck_v1.md',
    ]
    return all(p.exists() for p in needed)


def player_score():
    data = load_json(PLAYER_SCORE_PATH, {})
    if 'weightedScore' in data:
        return data.get('weightedScore')
    return (data.get('compositeScore') or {}).get('overall')


def decide_next():
    gate = load_json(GATE_PATH, {})
    score = player_score()

    if not (ROOT / 'work' / 'pm' / 'daily_plan_2026-03-10.md').exists():
        return 'pm', 'PM 基线未建立，先由 PM 建立当日计划'

    if not planner_ready():
        return 'planner', '策划正式产物未齐套，进入 Planner'

    if gate.get('passed') is not True:
        return 'planner', '策划闸门未通过，回到 Planner 修订'

    if score is None:
        return 'player', '已有策划齐套产物但暂无玩家评分，进入 Player 复评'

    if score < 9.0:
        return 'planner', f'玩家评分 {score} < 9.0，回到 Planner 修订'

    dev_status = ROOT / 'work' / 'developer' / 'dev_status.md'
    if not dev_status.exists():
        return 'designer', f'玩家评分 {score} >= 9.0，先解锁 Designer'

    qa_plan = ROOT / 'work' / 'qa' / 'test_plan.md'
    if not qa_plan.exists():
        return 'developer', f'玩家评分 {score} >= 9.0，解锁 Developer'

    return 'qa', '存在开发产物，转入 QA 检查'


def apply_state(role, reason):
    state = load_json(STATE_PATH, {})
    state.update({
        'updatedAt': now_str(),
        'currentRole': role,
        'reason': reason,
        'scoreGate': 9.0,
        'designerFrozen': role not in ['designer', 'developer', 'qa'] and (player_score() is None or player_score() < 9.0),
        'developerFrozen': role not in ['designer', 'developer', 'qa'] and (player_score() is None or player_score() < 9.0),
        'qaFrozen': role not in ['qa'] and (player_score() is None or player_score() < 9.0),
    })
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '
', encoding='utf-8')

    PM_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PM_STATUS_PATH.write_text(
        '
'.join([
            '# PM 调度状态',
            '',
            f'- 更新时间：{state["updatedAt"]}',
            f'- 当前激活角色：{role}',
            f'- 触发原因：{reason}',
            '- 当前流程：PM -> Planner -> Player -> Designer -> Developer -> QA -> Sound',
            f'- 设计/开发/测试状态：{"冻结" if (player_score() is None or player_score() < 9.0) else "已解锁"}（需玩家评分 >= 9.0）',
            '- 音效状态：默认冻结，按需手动解锁',
        ]) + '
',
        encoding='utf-8'
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    role, reason = decide_next()
    result = {'nextRole': role, 'reason': reason, 'checkedAt': now_str()}
    if args.apply:
        apply_state(role, reason)
        result['applied'] = True
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
