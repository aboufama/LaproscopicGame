extends Node2D

@onready var left_instrument := $PortLeft/InstrumentLeft
@onready var right_instrument := $PortRight/InstrumentRight

signal tissue_contact()

func _ready() -> void:
    left_instrument.is_left = true
    right_instrument.is_left = false
    _update_ports()
    left_instrument.tissue_contact.connect(_on_tissue_contact)
    right_instrument.tissue_contact.connect(_on_tissue_contact)

func _process(_delta: float) -> void:
    _update_ports()

func _update_ports() -> void:
    left_instrument.set_port_position($PortLeft.global_position)
    right_instrument.set_port_position($PortRight.global_position)

func get_left_tip() -> Vector2:
    return left_instrument.get_tip_position()

func get_right_tip() -> Vector2:
    return right_instrument.get_tip_position()

func _on_tissue_contact() -> void:
    emit_signal("tissue_contact")
