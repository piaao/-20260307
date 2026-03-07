extends Node

var flow_steps: Array[String] = ["政务处理", "开堂办案", "颁布政令", "建设县城"]
var current_step: int = 0

func _ready() -> void:
	print("AncientMagistrate flow ready")
	print("Current step: %s" % flow_steps[current_step])

func next_step() -> void:
	current_step = (current_step + 1) % flow_steps.size()
	print("Current step: %s" % flow_steps[current_step])
