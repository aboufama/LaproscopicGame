extends Node

var current_drill: String = ""
var last_result: Dictionary = {}
var elapsed_time := 0.0
var _drill_start := 0.0

signal drill_started(id: String)
signal drill_finished(result: Dictionary)
signal request_scene(path: String)

func start_drill(id: String, scene_path: String) -> void:
    current_drill = id
    last_result = {}
    elapsed_time = 0.0
    _drill_start = Time.get_ticks_msec() / 1000.0
    emit_signal("request_scene", scene_path)
    emit_signal("drill_started", id)

func finish_drill(result: Dictionary) -> void:
    last_result = result
    current_drill = ""
    elapsed_time = 0.0
    emit_signal("drill_finished", result)

func elapsed_in_drill() -> float:
    if current_drill == "":
        return 0.0
    return Time.get_ticks_msec() / 1000.0 - _drill_start

func goto_scene(scene_path: String) -> void:
    emit_signal("request_scene", scene_path)
