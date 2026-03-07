extends Node

var daily_flow = ["政务处理", "开堂办案", "颁布政令", "建设县城"]
var flow_index = 0

func _ready() -> void:
	print("AncientMagistrate game flow initialized")
	print("Current step: %s" % daily_flow[flow_index])

func next_step() -> void:
	flow_index = (flow_index + 1) % daily_flow.size()
	print("Current step: %s" % daily_flow[flow_index])
