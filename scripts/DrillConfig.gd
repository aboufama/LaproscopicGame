extends Resource
class_name DrillConfig

@export var title: String = "Unnamed Drill"
@export var duration_s: float = 60.0
@export var target_drops: int = 12
@export var feeder_start_interval: float = 2.0
@export var feeder_end_interval: float = 1.0
@export var interval_curve: Curve
@export var aperture_defs: Array[Dictionary] = []
@export var penalties := {
    "tissue_touch": 5,
    "missed_drop": 8,
    "lost_bead": 10,
    "late_catch": 2
}
@export var scoring := {
    "streak_per3": 0.05,
    "streak_cap": 1.5,
    "economy_weight": 0.25
}
@export var constraints := {
    "fulcrum_inversion": true,
    "tremor_amp": 0.0,
    "contact_tolerance": 4.0
}
