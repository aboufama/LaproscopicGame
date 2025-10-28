extends RigidBody2D

signal dropped(aperture_id: String, perfect: bool)
signal fell_out()

func _ready() -> void:
    add_to_group("bead")
    gravity_scale = 2.5

func on_drop(aperture_id: String, perfect: bool) -> void:
    emit_signal("dropped", aperture_id, perfect)
    queue_free()

func _on_screen_exited() -> void:
    emit_signal("fell_out")
    queue_free()
