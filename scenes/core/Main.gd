extends Node

@onready var viewport_container := $SubViewportContainer
@onready var hud_layer := $CanvasLayer
@onready var sub_viewport := $SubViewportContainer/SubViewport

func _ready() -> void:
    GameState.connect("request_scene", Callable(self, "_on_request_scene"))
    GameState.connect("drill_finished", Callable(self, "_on_drill_finished"))
    _show_scene("res://ui/Menus/Title.tscn")

func _on_request_scene(path: String) -> void:
    _show_scene(path)

func _on_drill_finished(_result: Dictionary) -> void:
    hud_layer.call("show_results", GameState.last_result)

func _show_scene(path: String) -> void:
    var resource := load(path)
    if not resource:
        push_warning("Unable to load scene %s" % path)
        return
    for child in sub_viewport.get_children():
        child.queue_free()
    var inst := resource.instantiate()
    sub_viewport.add_child(inst)
    if inst.has_method("set_hud"):
        inst.call("set_hud", hud_layer)
    if inst.is_in_group("drill"):
        hud_layer.call("enter_drill", inst)
    else:
        hud_layer.call("exit_drill")
