class_name StateCenter
extends RefCounted

const DEFAULT_METRICS := {
	"heart": 60,
	"treasury": 200,
	"order": 55,
	"prestige": 40
}

const NATURAL_TICK := {
	"heart": -2,
	"treasury": 50,
	"order": -1,
	"prestige": 0
}

const THRESHOLDS := {
	"heart_redline": 30,
	"treasury_redline": 50,
	"order_redline": 40,
	"prestige_redline": 20
}

var day: int = 1
var metrics: Dictionary = {}
var history: Array = []

func _init() -> void:
	metrics = DEFAULT_METRICS.duplicate(true)

func apply_natural_tick() -> Dictionary:
	return apply_delta("natural_tick", NATURAL_TICK)

func apply_delta(source: String, delta: Dictionary) -> Dictionary:
	var applied: Dictionary = {}
	for key in delta.keys():
		if not metrics.has(key):
			continue
		var before: int = int(metrics[key])
		var raw_after: int = before + int(delta[key])
		var after: int = _clamp_metric(key, raw_after)
		metrics[key] = after
		applied[key] = after - before

	history.append({
		"day": day,
		"source": source,
		"delta": applied.duplicate(true),
		"snapshot": metrics.duplicate(true)
	})
	return applied

func next_day() -> void:
	day += 1

func get_snapshot() -> Dictionary:
	return {
		"day": day,
		"metrics": metrics.duplicate(true)
	}

func get_history(limit: int = 20) -> Array:
	if limit <= 0:
		return history.duplicate(true)
	var from_index: int = maxi(0, history.size() - limit)
	return history.slice(from_index, history.size())

func check_thresholds() -> Array:
	var alerts: Array = []
	if int(metrics["heart"]) < int(THRESHOLDS["heart_redline"]):
		alerts.append("民心低于红线：触发民怨链事件")
	if int(metrics["treasury"]) < int(THRESHOLDS["treasury_redline"]):
		alerts.append("库银低于红线：触发财政危机")
	if int(metrics["order"]) < int(THRESHOLDS["order_redline"]):
		alerts.append("秩序低于红线：触发治安危机")
	if int(metrics["prestige"]) < int(THRESHOLDS["prestige_redline"]):
		alerts.append("威望低于红线：晋升速度下降")
	return alerts

func _clamp_metric(metric_key: String, value: int) -> int:
	if metric_key == "treasury":
		return maxi(0, value)
	return clampi(value, 0, 100)
