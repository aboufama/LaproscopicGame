extends Node2D

signal grasp_started(bead)
signal grasp_released()
signal tissue_contact()

@export var speed := 480.0
@export var is_left := true
@export var fulcrum_inversion := true

@onready var tip: Area2D = $Tip
var port_position := Vector2.ZERO
var held_body: Node = null

func _ready() -> void:
    Config.setting_changed.connect(_on_setting_changed)
    _apply_settings()
    tip.body_entered.connect(_on_body_entered)
    tip.body_exited.connect(_on_body_exited)

func set_port_position(pos: Vector2) -> void:
    port_position = pos

func _physics_process(delta: float) -> void:
    var input_vector := _read_input()
    if input_vector.length() > 1.0:
        input_vector = input_vector.normalized()
    var movement := input_vector * speed * delta
    if fulcrum_inversion:
        movement = _apply_fulcrum(movement)
    var tremor := Config.get_setting("tremor_amp", 0.0)
    if tremor > 0.0:
        movement += Vector2(randf() - 0.5, randf() - 0.5) * tremor
    global_position += movement
    if held_body and is_instance_valid(held_body):
        held_body.global_position = tip.global_position
        held_body.linear_velocity = Vector2.ZERO
    _update_grip_state()

func _apply_fulcrum(vec: Vector2) -> Vector2:
    var to_tip := global_position - port_position
    if to_tip.length() <= 0.1:
        return vec
    var angle := to_tip.angle()
    var local := vec.rotated(-angle)
    local.x = -local.x
    return local.rotated(angle)

func _read_input() -> Vector2:
    if is_left:
        return Vector2(
            Input.get_action_strength("inst_left_right") - Input.get_action_strength("inst_left_left"),
            Input.get_action_strength("inst_left_down") - Input.get_action_strength("inst_left_up")
        )
    return Vector2(
        Input.get_action_strength("inst_right_right") - Input.get_action_strength("inst_right_left"),
        Input.get_action_strength("inst_right_down") - Input.get_action_strength("inst_right_up")
    )

func _update_grip_state() -> void:
    var action := is_left ? "grip_left" : "grip_right"
    if Input.is_action_just_pressed(action):
        _attempt_grasp()
    elif Input.is_action_just_released(action):
        _release_grasp()

func _attempt_grasp() -> void:
    if held_body:
        return
    var bodies := tip.get_overlapping_bodies()
    for body in bodies:
        if body.is_in_group("bead"):
            held_body = body
            body.set_deferred("linear_velocity", Vector2.ZERO)
            emit_signal("grasp_started", body)
            return

func _release_grasp() -> void:
    if not held_body:
        return
    emit_signal("grasp_released")
    held_body = null

func _on_body_entered(body: Node) -> void:
    if body.is_in_group("tissue"):
        emit_signal("tissue_contact")

func _on_body_exited(_body: Node) -> void:
    pass

func _apply_settings() -> void:
    fulcrum_inversion = Config.get_setting("fulcrum_inversion", true)

func _on_setting_changed(name: String, value) -> void:
    if name == "fulcrum_inversion":
        fulcrum_inversion = bool(value)

func get_tip_position() -> Vector2:
    return tip.global_position

