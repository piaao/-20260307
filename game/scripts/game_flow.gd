extends Node

const StateCenterScript = preload("res://scripts/state_center.gd")

const LOOP_STEPS := ["政务处理", "开堂办案", "颁布政令", "建设县城"]

var flow_index: int = 0
var state_center = StateCenterScript.new()
var policy_table: Dictionary = {}
var build_table: Dictionary = {}
var case_table: Dictionary = {}
var event_table: Dictionary = {}
var building_levels: Dictionary = {}
var runtime_flags: Dictionary = {
	"is_summer": false,
	"epidemic_risk": false,
	"night_patrol_failed_twice": false,
	"continuous_hot_days": 0,
	"is_month_end_week": false,
	"is_mid_case_week": false,
	"is_disaster_week": false,
	"wrong_judgment_rate": 0.0
}
var last_event_id: String = ""
var day_event_pick_count: int = 0
var event_last_trigger_day: Dictionary = {}
var event_type_last_trigger_day: Dictionary = {}
var weekly_type_counts: Dictionary = {}
var balance_rows: Array = []
var policy_delayed_table: Dictionary = {}
var build_weekly_bonus_table: Dictionary = {}
var threshold_rules: Dictionary = {}
var weekly_treasury_net_history: Array = []
var week_start_treasury: int = 0
var rank_tier: String = "九品"
var monthly_reports: Array = []

func _ready() -> void:
	_load_config_tables()
	_print_bootstrap()

func set_runtime_flags(flags: Dictionary) -> void:
	for key in flags.keys():
		runtime_flags[str(key)] = flags[key]

func current_step() -> String:
	return LOOP_STEPS[flow_index]

func next_step() -> String:
	flow_index = (flow_index + 1) % LOOP_STEPS.size()
	return current_step()

func run_current_step(action_id: String = "") -> Dictionary:
	var step := current_step()
	var result := {
		"step": step,
		"action_id": action_id,
		"applied": {},
		"alerts": []
	}

	match step:
		"政务处理":
			result["applied"] = state_center.apply_natural_tick()
		"开堂办案":
			if action_id.is_empty() and case_table.size() > 0:
				action_id = str(case_table.keys()[0])
			result["action_id"] = action_id
			result["applied"] = _resolve_case(action_id, true)
		"颁布政令":
			if action_id.is_empty() and policy_table.size() > 0:
				action_id = str(policy_table.keys()[0])
			result["action_id"] = action_id
			result["applied"] = _apply_policy(action_id)
		"建设县城":
			if action_id.is_empty() and build_table.size() > 0:
				action_id = str(build_table.keys()[0])
			result["action_id"] = action_id
			result["applied"] = _apply_build(action_id)

	result["alerts"] = state_center.check_thresholds()
	_print_step_result(result)
	return result

func complete_cycle() -> Dictionary:
	var cycle_results: Array = []
	for _index in LOOP_STEPS.size():
		cycle_results.append(run_current_step())
		next_step()

	var day_summary := _start_next_day()
	var snapshot := state_center.get_snapshot()
	print("[Cycle] End of day snapshot: %s" % [snapshot])
	return {
		"results": cycle_results,
		"day_summary": day_summary,
		"snapshot": snapshot
	}

func _apply_policy(policy_id: String) -> Dictionary:
	if not policy_table.has(policy_id):
		push_warning("Policy not found: %s" % policy_id)
		return {}
	var policy: Dictionary = policy_table[policy_id]
	var delta: Dictionary = policy.get("instant_delta", {})
	var applied := state_center.apply_delta("policy:%s" % policy_id, delta)
	_schedule_policy_delayed(policy_id)
	return applied

func _apply_build(build_id: String) -> Dictionary:
	if not build_table.has(build_id):
		push_warning("Build not found: %s" % build_id)
		return {}

	var build_item: Dictionary = build_table[build_id]
	var current_level: int = int(building_levels.get(build_id, 1))
	var max_level: int = int(build_item.get("max_level", 3))
	if current_level >= max_level:
		return {}

	var target_level := current_level + 1
	var cost_key := "cost_l%d" % target_level
	var cost: int = int(build_item.get(cost_key, 0))
	if int(state_center.metrics.get("treasury", 0)) < cost:
		push_warning("Not enough treasury for build: %s" % build_id)
		return {}

	var delta: Dictionary = {"treasury": -cost}
	if build_item.has("instant_delta"):
		for metric in build_item["instant_delta"].keys():
			delta[metric] = int(build_item["instant_delta"][metric])

	building_levels[build_id] = target_level
	return state_center.apply_delta("build:%s_l%d" % [build_id, target_level], delta)

func _resolve_case(case_id: String, success: bool) -> Dictionary:
	if not case_table.has(case_id):
		push_warning("Case not found: %s" % case_id)
		return {}

	var case_item: Dictionary = case_table[case_id]
	var delta: Dictionary = case_item.get("success_delta" if success else "fail_delta", {})
	var result_tag := "success" if success else "fail"
	return state_center.apply_delta("case:%s:%s" % [case_id, result_tag], delta)

func _load_config_tables() -> void:
	policy_table = _load_json_table("res://data/policy.json", "policy_id")
	build_table = _load_json_table("res://data/buildings.json", "build_id")
	case_table = _load_json_table("res://data/cases.json", "case_id")
	event_table = _load_event_table("work/planner/event_table_v1.md")
	balance_rows = _load_balance_sheet("work/planner/balance_sheet_v1.csv")
	_apply_balance_overrides(balance_rows)
	_apply_threshold_rules_from_balance()

	for build_id in build_table.keys():
		building_levels[build_id] = 1

	week_start_treasury = int(state_center.metrics.get("treasury", 0))

func _load_json_table(path: String, id_key: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_warning("Config missing: %s" % path)
		return {}

	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_warning("Config open failed: %s" % path)
		return {}

	var raw := file.get_as_text()
	var parsed = JSON.parse_string(raw)
	if typeof(parsed) != TYPE_ARRAY:
		push_warning("Config format invalid (array expected): %s" % path)
		return {}

	var table: Dictionary = {}
	for item in parsed:
		if typeof(item) == TYPE_DICTIONARY and item.has(id_key):
			table[str(item[id_key])] = item
	return table

func _load_balance_sheet(path: String) -> Array:
	var abs_path := ProjectSettings.globalize_path("res://../" + path)
	if not FileAccess.file_exists(abs_path):
		push_warning("Balance sheet missing: %s" % abs_path)
		return []

	var file := FileAccess.open(abs_path, FileAccess.READ)
	if file == null:
		push_warning("Balance sheet open failed: %s" % abs_path)
		return []

	if file.eof_reached():
		return []

	var headers_line := file.get_line().strip_edges()
	if headers_line.is_empty():
		return []

	var headers := headers_line.split(",", false)
	var rows: Array = []
	while not file.eof_reached():
		var line := file.get_line().strip_edges()
		if line.is_empty():
			continue
		var cols := line.split(",", true)
		if cols.size() < headers.size():
			continue
		var row: Dictionary = {}
		for index in headers.size():
			row[str(headers[index]).strip_edges()] = str(cols[index]).strip_edges()
		rows.append(row)
	return rows

func _apply_balance_overrides(rows: Array) -> void:
	policy_delayed_table.clear()
	build_weekly_bonus_table.clear()
	threshold_rules.clear()

	for row_any in rows:
		if typeof(row_any) != TYPE_DICTIONARY:
			continue
		var row: Dictionary = row_any
		var module := str(row.get("module", "")).strip_edges()
		var item_id := str(row.get("item_id", "")).strip_edges()
		var rule := str(row.get("formula_or_rule", "")).strip_edges()
		if module.is_empty() or item_id.is_empty() or rule.is_empty():
			continue

		if module == "policy" and policy_table.has(item_id):
			var parsed_policy := _parse_policy_rule(rule)
			var policy_item: Dictionary = policy_table[item_id]
			var instant_delta: Dictionary = parsed_policy.get("instant", {})
			if not instant_delta.is_empty():
				policy_item["instant_delta"] = instant_delta
				policy_table[item_id] = policy_item
			var delayed_list: Array = parsed_policy.get("delayed", [])
			if not delayed_list.is_empty():
				policy_delayed_table[item_id] = delayed_list
			continue

		if module == "build" and build_table.has(item_id):
			var parsed_build := _parse_build_rule(rule)
			var build_item: Dictionary = build_table[item_id]
			var costs: Dictionary = parsed_build.get("costs", {})
			for cost_key in costs.keys():
				build_item[str(cost_key)] = int(costs[cost_key])
			build_table[item_id] = build_item

			var weekly_bonus: Dictionary = parsed_build.get("weekly_bonus", {})
			if not weekly_bonus.is_empty():
				build_weekly_bonus_table[item_id] = weekly_bonus
			continue

		if module == "case" and case_table.has(item_id):
			var parsed_case := _parse_case_rule(rule)
			var case_item: Dictionary = case_table[item_id]
			var success_delta: Dictionary = parsed_case.get("success_delta", {})
			var fail_delta: Dictionary = parsed_case.get("fail_delta", {})
			if not success_delta.is_empty():
				case_item["success_delta"] = success_delta
			if not fail_delta.is_empty():
				case_item["fail_delta"] = fail_delta
			case_table[item_id] = case_item
			continue

		if module == "threshold":
			threshold_rules[item_id] = rule

func _parse_policy_rule(rule_text: String) -> Dictionary:
	var parsed := {
		"instant": {},
		"delayed": []
	}
	if rule_text.is_empty():
		return parsed

	for raw_segment in rule_text.split(";"):
		var segment := raw_segment.strip_edges()
		if segment.is_empty():
			continue

		if segment.begins_with("day"):
			var day_text := segment.substr(3, segment.find(":") - 3)
			var delay_days := _extract_first_integer(day_text)
			if delay_days <= 0:
				continue
			var payload := segment.substr(segment.find(":") + 1).strip_edges()
			var delayed_item := _parse_rule_metric_token(payload, "treasury")
			if delayed_item.is_empty():
				continue
			parsed["delayed"].append({
				"delay_days": delay_days,
				"delta": {delayed_item["key"]: int(delayed_item["value"])}
			})
			continue

		var instant_token := segment
		if instant_token.begins_with("instant:"):
			instant_token = instant_token.trim_prefix("instant:").strip_edges()
		var instant_item := _parse_rule_metric_token(instant_token)
		if instant_item.is_empty():
			continue
		var instant_delta: Dictionary = parsed["instant"]
		instant_delta[instant_item["key"]] = int(instant_item["value"])
		parsed["instant"] = instant_delta

	return parsed

func _parse_build_rule(rule_text: String) -> Dictionary:
	var parsed := {
		"costs": {},
		"weekly_bonus": {}
	}
	if rule_text.is_empty():
		return parsed

	for raw_segment in rule_text.split(";"):
		var segment := raw_segment.strip_edges()
		if segment.is_empty():
			continue

		if segment.begins_with("cost_l") and segment.find("=") != -1:
			var parts := segment.split("=", false)
			if parts.size() == 2:
				parsed["costs"][parts[0].strip_edges()] = _extract_first_integer(parts[1])
			continue

		if segment.begins_with("bonus="):
			var bonus_rule := segment.trim_prefix("bonus=")
			if bonus_rule.find("week_tax+") != -1:
				parsed["weekly_bonus"] = {
					"metric": "treasury",
					"percent": _extract_first_integer(bonus_rule)
				}

	return parsed

func _parse_case_rule(rule_text: String) -> Dictionary:
	var parsed := {
		"success_delta": {},
		"fail_delta": {}
	}
	if rule_text.is_empty():
		return parsed

	for raw_segment in rule_text.split(";"):
		var segment := raw_segment.strip_edges()
		if segment.is_empty():
			continue

		if segment.begins_with("success:"):
			var success_payload := segment.trim_prefix("success:")
			var success_item := _parse_rule_metric_token(success_payload)
			if not success_item.is_empty():
				var success_delta: Dictionary = parsed["success_delta"]
				success_delta[success_item["key"]] = int(success_item["value"])
				parsed["success_delta"] = success_delta
			continue

		if segment.begins_with("fail:"):
			var fail_payload := segment.trim_prefix("fail:")
			var fail_item := _parse_rule_metric_token(fail_payload)
			if not fail_item.is_empty():
				var fail_delta: Dictionary = parsed["fail_delta"]
				fail_delta[fail_item["key"]] = int(fail_item["value"])
				parsed["fail_delta"] = fail_delta

	return parsed

func _parse_rule_metric_token(token: String, default_key: String = "") -> Dictionary:
	var clean_token := token.strip_edges()
	if clean_token.is_empty():
		return {}

	var key := _normalize_metric_key(clean_token)
	if key.is_empty() and not default_key.is_empty():
		key = _normalize_metric_key(default_key)
	if key.is_empty():
		return {}

	var value := _extract_signed_value(clean_token)
	if clean_token.find("+") == -1 and clean_token.find("-") == -1:
		value = _extract_first_integer(clean_token)

	return {
		"key": key,
		"value": value
	}

func _normalize_metric_key(token: String) -> String:
	if token.find("heart") != -1 or token.find("民心") != -1:
		return "heart"
	if token.find("treasury") != -1 or token.find("库银") != -1 or token.find("week_tax") != -1:
		return "treasury"
	if token.find("order") != -1 or token.find("秩序") != -1:
		return "order"
	if token.find("prestige") != -1 or token.find("威望") != -1:
		return "prestige"
	return ""

func _load_event_table(path: String) -> Dictionary:
	var abs_path := ProjectSettings.globalize_path("res://../" + path)
	if not FileAccess.file_exists(abs_path):
		push_warning("Event table missing: %s" % abs_path)
		return {}

	var file := FileAccess.open(abs_path, FileAccess.READ)
	if file == null:
		push_warning("Event table open failed: %s" % abs_path)
		return {}

	var table: Dictionary = {}
	while not file.eof_reached():
		var line := file.get_line().strip_edges()
		if not line.begins_with("| EVT"):
			continue
		var cols := line.split("|")
		if cols.size() < 10:
			continue
		var event_id := cols[1].strip_edges()
		if event_id.is_empty():
			continue
		table[event_id] = {
			"type": cols[2].strip_edges(),
			"condition": cols[3].strip_edges(),
			"weight": int(cols[4].strip_edges()),
			"cooldown": int(cols[5].strip_edges()),
			"effect": cols[8].strip_edges(),
			"case_id": cols[9].strip_edges()
		}

	return table

func _schedule_policy_delayed(policy_id: String) -> void:
	if policy_delayed_table.has(policy_id):
		var delayed_items: Array = policy_delayed_table[policy_id]
		for item_any in delayed_items:
			if typeof(item_any) != TYPE_DICTIONARY:
				continue
			var item: Dictionary = item_any
			var delay_days: int = int(item.get("delay_days", 0))
			var delta: Dictionary = item.get("delta", {})
			if delay_days <= 0 or delta.is_empty():
				continue
			state_center.schedule_delta("policy:%s:day%d" % [policy_id, delay_days], delta, delay_days)
		return

	match policy_id:
		"POL004":
			state_center.schedule_delta("policy:POL004:day3", {"treasury": 20}, 3)
			state_center.schedule_delta("policy:POL004:day7", {"treasury": 45}, 7)
		"POL006":
			state_center.schedule_delta("policy:POL006:day7", {"treasury": 11}, 7)
		_:
			return

func _start_next_day() -> Dictionary:
	var day_advance := state_center.advance_day()
	day_event_pick_count = 0

	var weekly_summary: Dictionary = {}
	var monthly_summary: Dictionary = {}
	if _is_week_boundary_day():
		weekly_summary = _apply_weekly_settlement()
	if _is_month_boundary_day():
		monthly_summary = _apply_monthly_settlement()

	var event_result := _trigger_daily_event_if_needed()
	return {
		"day_advance": day_advance,
		"weekly_summary": weekly_summary,
		"monthly_summary": monthly_summary,
		"event_result": event_result,
		"rank_tier": rank_tier
	}

func _is_week_boundary_day() -> bool:
	return int((int(state_center.day) - 1) % 7) == 0

func _is_month_boundary_day() -> bool:
	return int((int(state_center.day) - 1) % 28) == 0

func _apply_weekly_settlement() -> Dictionary:
	var current_treasury: int = int(state_center.metrics.get("treasury", 0))
	var treasury_net: int = current_treasury - week_start_treasury
	weekly_treasury_net_history.append(treasury_net)

	var weekly_bonus_applied: Dictionary = _collect_weekly_build_bonus(treasury_net)
	if not weekly_bonus_applied.is_empty():
		state_center.apply_delta("weekly:build_bonus", weekly_bonus_applied)

	week_start_treasury = int(state_center.metrics.get("treasury", 0))
	var previous_rank := rank_tier
	rank_tier = _evaluate_rank_tier()

	return {
		"week_index": int((int(state_center.day) - 1) / 7),
		"treasury_net": treasury_net,
		"build_bonus": weekly_bonus_applied,
		"rank_before": previous_rank,
		"rank_after": rank_tier
	}

func _collect_weekly_build_bonus(treasury_net: int) -> Dictionary:
	var bonus_total: Dictionary = {}
	if treasury_net <= 0:
		return bonus_total

	for build_id in build_weekly_bonus_table.keys():
		if int(building_levels.get(build_id, 1)) < 2:
			continue
		var bonus_rule: Dictionary = build_weekly_bonus_table[build_id]
		var metric := str(bonus_rule.get("metric", ""))
		var percent: int = int(bonus_rule.get("percent", 0))
		if metric.is_empty() or percent <= 0:
			continue
		var value: int = int(round(float(treasury_net * percent) / 100.0))
		if value <= 0:
			continue
		bonus_total[metric] = int(bonus_total.get(metric, 0)) + value

	return bonus_total

func _apply_monthly_settlement() -> Dictionary:
	var recent_weekly: Array = []
	var from_index: int = maxi(0, weekly_treasury_net_history.size() - 4)
	recent_weekly = weekly_treasury_net_history.slice(from_index, weekly_treasury_net_history.size())

	var snapshot := state_center.get_snapshot()
	var report := {
		"month_index": int((int(state_center.day) - 1) / 28),
		"rank_tier": rank_tier,
		"weekly_treasury_net": recent_weekly,
		"snapshot": snapshot
	}
	monthly_reports.append(report)
	return report

func _evaluate_rank_tier() -> String:
	if _has_two_consecutive_positive_weeks():
		return "七品"
	if _is_rank_eight_condition_met():
		if rank_tier == "七品":
			return rank_tier
		return "八品"
	return rank_tier

func _is_rank_eight_condition_met() -> bool:
	var heart: int = int(state_center.metrics.get("heart", 0))
	var order: int = int(state_center.metrics.get("order", 0))
	return heart >= 60 and order >= 55

func _has_two_consecutive_positive_weeks() -> bool:
	if weekly_treasury_net_history.size() < 2:
		return false
	var last_index := weekly_treasury_net_history.size() - 1
	var current_week: int = int(weekly_treasury_net_history[last_index])
	var previous_week: int = int(weekly_treasury_net_history[last_index - 1])
	return current_week > 0 and previous_week > 0

func _apply_threshold_rules_from_balance() -> void:
	var thresholds := state_center.get_thresholds()
	for rule_id in threshold_rules.keys():
		var rule_text := str(threshold_rules[rule_id])
		if rule_text.find("heart<") != -1:
			thresholds["heart_redline"] = _extract_first_integer(rule_text)
		elif rule_text.find("treasury<") != -1:
			thresholds["treasury_redline"] = _extract_first_integer(rule_text)
		elif rule_text.find("order<") != -1:
			thresholds["order_redline"] = _extract_first_integer(rule_text)
		elif rule_text.find("prestige<") != -1:
			thresholds["prestige_redline"] = _extract_first_integer(rule_text)
	state_center.set_thresholds(thresholds)

func _trigger_daily_event_if_needed() -> Dictionary:
	if event_table.is_empty():
		return {}
	if day_event_pick_count >= 1:
		return {}

	var selected_event_id := _select_event_id()
	if selected_event_id.is_empty():
		return {}

	var event_item: Dictionary = event_table[selected_event_id]
	var payload := _parse_event_effect_payload(event_item.get("effect", ""), true)
	var instant_delta: Dictionary = payload.get("instant", {})
	var applied := state_center.apply_delta("event:%s:A" % selected_event_id, instant_delta)
	var delayed_list: Array = payload.get("delayed", [])
	for delayed_item in delayed_list:
		if typeof(delayed_item) != TYPE_DICTIONARY:
			continue
		var delay_days: int = int(delayed_item.get("delay_days", 0))
		var delayed_delta: Dictionary = delayed_item.get("delta", {})
		if delay_days <= 0 or delayed_delta.is_empty():
			continue
		state_center.schedule_delta("event:%s:A:day%d" % [selected_event_id, delay_days], delayed_delta, delay_days)

	_update_event_counters(selected_event_id, event_item)
	day_event_pick_count += 1
	last_event_id = selected_event_id
	return {
		"event_id": selected_event_id,
		"option": "A",
		"applied": applied,
		"linked_case": str(event_item.get("case_id", "")),
		"scheduled_count": delayed_list.size()
	}

func _select_event_id() -> String:
	var candidates: Array = []
	for event_id in event_table.keys():
		if event_id == last_event_id:
			continue
		var event_item: Dictionary = event_table[event_id]
		if not _is_event_available(str(event_id), event_item):
			continue
		if not _check_event_condition(str(event_item.get("condition", ""))):
			continue
		candidates.append({
			"event_id": event_id,
			"weight": _compute_event_weight(str(event_id), event_item)
		})

	if candidates.is_empty():
		return ""

	candidates.sort_custom(func(a, b): return int(a["weight"]) > int(b["weight"]))
	return str(candidates[0]["event_id"])

func _check_event_condition(condition_text: String) -> bool:
	if condition_text.is_empty():
		return true

	var segments := condition_text.split("且")
	for raw_segment in segments:
		var segment := raw_segment.strip_edges()
		if segment.is_empty():
			continue
		if not _check_condition_segment(segment):
			return false
	return true

func _check_condition_segment(segment: String) -> bool:
	var metric_key := _metric_key_from_condition(segment)
	if not metric_key.is_empty():
		return _evaluate_numeric_condition(int(state_center.metrics.get(metric_key, 0)), segment)

	var build_id := _build_id_from_condition(segment)
	if not build_id.is_empty():
		return _evaluate_numeric_condition(int(building_levels.get(build_id, 1)), segment)

	match segment:
		"入夏":
			return bool(runtime_flags.get("is_summer", false))
		"疫情苗头":
			return bool(runtime_flags.get("epidemic_risk", false))
		"夜巡连续失败2次":
			return bool(runtime_flags.get("night_patrol_failed_twice", false))
		"中级案件周":
			return bool(runtime_flags.get("is_mid_case_week", false))
		"月末考核周":
			return bool(runtime_flags.get("is_month_end_week", false))
		"财政绿色":
			return int(state_center.metrics.get("treasury", 0)) >= 180
		"红色财政":
			return int(state_center.metrics.get("treasury", 0)) < 50
		"逢灾":
			return bool(runtime_flags.get("is_disaster_week", false))
		_:
			if segment.find("连续晴热") != -1:
				return int(runtime_flags.get("continuous_hot_days", 0)) >= _extract_threshold(segment)
			return false

func _metric_key_from_condition(text: String) -> String:
	if text.find("民心") != -1:
		return "heart"
	if text.find("库银") != -1:
		return "treasury"
	if text.find("秩序") != -1:
		return "order"
	if text.find("威望") != -1:
		return "prestige"
	return ""

func _build_id_from_condition(text: String) -> String:
	if text.find("县衙") != -1:
		return "BLD001"
	if text.find("粮仓") != -1:
		return "BLD002"
	if text.find("集市") != -1:
		return "BLD003"
	if text.find("巡防") != -1:
		return "BLD004"
	if text.find("医馆") != -1:
		return "BLD005"
	return ""

func _evaluate_numeric_condition(value: int, condition_text: String) -> bool:
	var threshold := _extract_threshold(condition_text)
	if condition_text.find(">=") != -1:
		return value >= threshold
	if condition_text.find("<=") != -1:
		return value <= threshold
	if condition_text.find(">") != -1:
		return value > threshold
	if condition_text.find("<") != -1:
		return value < threshold
	if condition_text.find("级") != -1:
		return value == threshold
	return true

func _is_event_available(event_id: String, event_item: Dictionary) -> bool:
	var current_day: int = int(state_center.day)
	var cooldown: int = int(event_item.get("cooldown", 0))
	if event_last_trigger_day.has(event_id):
		var last_day: int = int(event_last_trigger_day[event_id])
		if current_day - last_day < cooldown:
			return false

	var event_type := str(event_item.get("type", ""))
	if event_type_last_trigger_day.has(event_type):
		var last_type_day: int = int(event_type_last_trigger_day[event_type])
		if current_day - last_type_day < 2:
			return false

	if event_type == "天灾":
		var week_index: int = int((current_day - 1) / 7)
		var week_key := "天灾:%d" % week_index
		if int(weekly_type_counts.get(week_key, 0)) >= 1:
			return false

	return true

func _compute_event_weight(event_id: String, event_item: Dictionary) -> int:
	var weight: int = int(event_item.get("weight", 1))
	if event_id == "EVT015" and int(state_center.metrics.get("treasury", 0)) < 50:
		weight += 15
	if float(runtime_flags.get("wrong_judgment_rate", 0.0)) > 20.0 and str(event_item.get("type", "")) == "官场":
		weight += 10
	return maxi(1, weight)

func _update_event_counters(event_id: String, event_item: Dictionary) -> void:
	var current_day: int = int(state_center.day)
	event_last_trigger_day[event_id] = current_day

	var event_type := str(event_item.get("type", ""))
	if not event_type.is_empty():
		event_type_last_trigger_day[event_type] = current_day
		if event_type == "天灾":
			var week_index: int = int((current_day - 1) / 7)
			var week_key := "天灾:%d" % week_index
			weekly_type_counts[week_key] = int(weekly_type_counts.get(week_key, 0)) + 1

func _extract_threshold(condition_text: String) -> int:
	return _extract_first_integer(condition_text)

func _extract_first_integer(text: String) -> int:
	var digits := ""
	var started := false
	for ch in text:
		if ch >= "0" and ch <= "9":
			digits += ch
			started = true
		elif started:
			break
	if digits.is_empty():
		return 0
	return int(digits)

func _parse_event_effect_payload(effect_text: String, use_option_a: bool) -> Dictionary:
	var payload := {
		"instant": {},
		"delayed": []
	}
	if effect_text.is_empty():
		return payload

	var option_parts := effect_text.split("；")
	var option_text := ""
	for part in option_parts:
		var clean_part := part.strip_edges()
		if use_option_a and clean_part.begins_with("A:"):
			option_text = clean_part.trim_prefix("A:")
			break
		if (not use_option_a) and clean_part.begins_with("B:"):
			option_text = clean_part.trim_prefix("B:")
			break

	if option_text.is_empty():
		option_text = option_parts[0].strip_edges()

	for item in option_text.split("/"):
		var token := item.strip_edges()
		if token.is_empty():
			continue
		var parsed := _parse_metric_delta(token)
		if parsed.size() == 2:
			var delay_days: int = _extract_delay_days(token)
			if delay_days > 0:
				payload["delayed"].append({
					"delay_days": delay_days,
					"delta": {parsed["key"]: parsed["value"]}
				})
			else:
				var instant: Dictionary = payload["instant"]
				instant[parsed["key"]] = int(instant.get(parsed["key"], 0)) + int(parsed["value"])
				payload["instant"] = instant
	return payload

func _parse_metric_delta(token: String) -> Dictionary:
	if token.find("民心") != -1:
		return {"key": "heart", "value": _extract_signed_value(token)}
	if token.find("库银") != -1:
		return {"key": "treasury", "value": _extract_signed_value(token)}
	if token.find("秩序") != -1:
		return {"key": "order", "value": _extract_signed_value(token)}
	if token.find("威望") != -1:
		return {"key": "prestige", "value": _extract_signed_value(token)}
	return {}

func _extract_signed_value(token: String) -> int:
	var sign: int = 1
	if token.find("-") != -1:
		sign = -1
	return sign * _extract_first_integer(token)

func _extract_delay_days(token: String) -> int:
	if token.find("周结算") != -1:
		return 7
	var left: int = token.find("(")
	var right: int = token.find("日后")
	if left == -1 or right == -1 or right <= left:
		return 0
	var delay_text := token.substr(left + 1, right - left - 1)
	return _extract_first_integer(delay_text)

func _print_bootstrap() -> void:
	print("AncientMagistrate core loop initialized")
	print("Current step: %s" % current_step())
	print("Policy count: %d" % policy_table.size())
	print("Build count: %d" % build_table.size())
	print("Case count: %d" % case_table.size())
	print("Event count: %d" % event_table.size())
	print("Snapshot: %s" % [state_center.get_snapshot()])

func _print_step_result(result: Dictionary) -> void:
	print("[Step] %s | Action=%s | Delta=%s" % [result.get("step", ""), result.get("action_id", ""), result.get("applied", {})])
	var alerts: Array = result.get("alerts", [])
	if alerts.size() > 0:
		print("[Alerts] %s" % [alerts])
