extends Area2D

signal bead_dropped(aperture_id: String, perfect: bool)

@export var aperture_id := "A"
@export var radius := 32.0
@export var moves := false
@export var path := "static"

@onready var shape: CollisionShape2D = $CollisionShape2D
@onready var ring: Node2D = $Ring

var _start_position := Vector2.ZERO
var _time := 0.0

func _ready() -> void:
    _start_position = position
    add_to_group("aperture")
    body_entered.connect(_on_body_entered)
    _apply_radius()

func _process(delta: float) -> void:
    if not moves:
        return
    _time += delta
    if path == "circle_slow":
        var offset := Vector2(0, 20).rotated(_time * 0.8)
        position = _start_position + offset
    elif path == "ping_pong":
        var phase := sin(_time)
        position = _start_position + Vector2(phase * 40.0, 0)

func _on_body_entered(body: Node) -> void:
    if not body.is_in_group("bead"):
        return
    var perfect := body.global_position.distance_to(global_position) <= radius * 0.35
    if body.has_method("on_drop"):
        body.call_deferred("on_drop", aperture_id, perfect)
    emit_signal("bead_dropped", aperture_id, perfect)

func _apply_radius() -> void:
    if shape and shape.shape is CircleShape2D:
        shape.shape.radius = radius
    if ring:
        var scale_factor := radius / 32.0
        ring.scale = Vector2(scale_factor, scale_factor)
