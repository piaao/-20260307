extends Node

const StateCenterScript = preload("res://scripts/state_center.gd")

const LOOP_STEPS := ["政务处理", "开堂办案", "颁布政令", "建设县城"]

var flow_index: int = 0
var state_center = StateCenterScript.new()
var policy_table: Dictionary = {}
var build_table: Dictionary = {}
var case_table: Dictionary = {}
var building_levels: Dictionary = {}

func _ready() -> void:
	_load_config_tables()
	_print_bootstrap()

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

	state_center.next_day()
	var snapshot := state_center.get_snapshot()
	print("[Cycle] End of day snapshot: %s" % [snapshot])
	return {
		"results": cycle_results,
		"snapshot": snapshot
	}

func _apply_policy(policy_id: String) -> Dictionary:
	if not policy_table.has(policy_id):
		push_warning("Policy not found: %s" % policy_id)
		return {}
	var policy: Dictionary = policy_table[policy_id]
	var delta: Dictionary = policy.get("instant_delta", {})
	return state_center.apply_delta("policy:%s" % policy_id, delta)

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

	for build_id in build_table.keys():
		building_levels[build_id] = 1

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

func _print_bootstrap() -> void:
	print("AncientMagistrate core loop initialized")
	print("Current step: %s" % current_step())
	print("Policy count: %d" % policy_table.size())
	print("Build count: %d" % build_table.size())
	print("Case count: %d" % case_table.size())
	print("Snapshot: %s" % [state_center.get_snapshot()])

func _print_step_result(result: Dictionary) -> void:
	print("[Step] %s | Action=%s | Delta=%s" % [result.get("step", ""), result.get("action_id", ""), result.get("applied", {})])
	var alerts: Array = result.get("alerts", [])
	if alerts.size() > 0:
		print("[Alerts] %s" % [alerts])
