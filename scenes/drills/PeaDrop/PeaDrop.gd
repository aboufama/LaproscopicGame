extends Node2D

@export var config: DrillConfig
@export_file("*.tres") var config_path := "res://data/drills/pea_drop_plus.tres"

@onready var rig := $LaparoscopeRig
@onready var feeder := $Feeder
@onready var aperture_root := $Apertures
@onready var tissue := $Tissue

const SCORE := preload("res://scripts/scoring/ScoreModel.gd")
const BEAD_SCENE := preload("res://scenes/drills/PeaDrop/Bead.tscn")
const APERTURE_SCENE := preload("res://scenes/drills/PeaDrop/Aperture.tscn")

var hud
var time_left := 0.0
var drops_done := 0
var contacts := 0
var streak := 0
var path_len_l := 0.0
var path_len_r := 0.0
var last_left := Vector2.ZERO
var last_right := Vector2.ZERO
var active_beads: Array = []
var running := false

func _ready() -> void:
    add_to_group("drill")
    if config == null and config_path != "":
        config = load(config_path)
    if config == null:
        push_warning("PeaDrop missing config")
        return
    feeder.setup(config)
    _build_apertures()
    rig.tissue_contact.connect(_on_tissue_contact)
    time_left = config.duration_s
    Telemetry.begin_session("pea_drop", config.title)
    running = true
    set_process(true)
    set_physics_process(true)

func set_hud(hud_node) -> void:
    hud = hud_node
    if hud:
        hud.call_deferred("update_drops", drops_done, config.target_drops)
        hud.call_deferred("update_timer", time_left)

func _process(delta: float) -> void:
    time_left = max(time_left - delta, 0.0)
    _update_paths()
    if hud:
        hud.update_timer(time_left)
    if feeder.advance(delta):
        _spawn_bead()
    if time_left <= 0.0:
        _end_session()

func _update_paths() -> void:
    var left_tip := rig.get_left_tip()
    var right_tip := rig.get_right_tip()
    if last_left != Vector2.ZERO:
        path_len_l += left_tip.distance_to(last_left)
    if last_right != Vector2.ZERO:
        path_len_r += right_tip.distance_to(last_right)
    last_left = left_tip
    last_right = right_tip

func _spawn_bead() -> void:
    var bead := BEAD_SCENE.instantiate()
    add_child(bead)
    bead.global_position = feeder.spawn_position()
    bead.dropped.connect(_on_bead_dropped.bind(bead))
    bead.fell_out.connect(_on_bead_lost.bind(bead))
    active_beads.append(bead)
    Telemetry.log_event({"evt": "bead_spawn", "pos": [bead.global_position.x, bead.global_position.y]})

func _build_apertures() -> void:
    for child in aperture_root.get_children():
        child.queue_free()
    for data in config.aperture_defs:
        var aperture = APERTURE_SCENE.instantiate()
        aperture.aperture_id = data.get("id", "A")
        aperture.radius = data.get("radius", 32.0) * Config.get_setting("aperture_scale", 1.0)
        aperture.moves = data.get("moves", false)
        aperture.path = data.get("path", "static")
        aperture.position = data.get("pos", Vector2.ZERO)
        aperture_root.add_child(aperture)
        aperture.bead_dropped.connect(_on_bead_dropped_from_aperture)

func _on_bead_dropped(aperture_id: String, perfect: bool, bead = null) -> void:
    if bead and bead in active_beads:
        active_beads.erase(bead)
    _on_bead_dropped_from_aperture(aperture_id, perfect)

func _on_bead_dropped_from_aperture(aperture_id: String, perfect: bool) -> void:
    drops_done += 1
    streak += 1
    var mult := SCORE.streak_multiplier(streak, config.scoring)
    Telemetry.log_event({"evt": "drop", "aperture": aperture_id, "perfect": perfect, "streak": streak, "mult": mult})
    if perfect:
        Sfx.perfect()
    else:
        Sfx.drop()
    if hud:
        hud.update_drops(drops_done, config.target_drops)
        hud.bump_streak(streak, mult)
    if drops_done >= config.target_drops:
        _end_session()

func _on_bead_lost(bead = null) -> void:
    if bead and bead in active_beads:
        active_beads.erase(bead)
    streak = 0
    SCORE.apply_penalty("lost_bead", config)
    Telemetry.log_event({"evt": "lost_bead"})
    if hud:
        hud.bump_streak(streak, 1.0)

func _on_tissue_contact() -> void:
    contacts += 1
    streak = 0
    SCORE.apply_penalty("tissue_touch", config)
    Telemetry.log_event({"evt": "tissue_touch", "count": contacts})
    if hud:
        hud.flash_error()
        hud.bump_streak(streak, 1.0)
    Sfx.buzz()

func _physics_process(_delta: float) -> void:
    var remaining: Array = []
    for bead in active_beads:
        if not is_instance_valid(bead):
            continue
        if bead.global_position.y > 600:
            bead.queue_free()
            continue
        remaining.append(bead)
    active_beads = remaining

func _end_session() -> void:
    if not running:
        return
    running = false
    set_process(false)
    set_physics_process(false)
    active_beads.clear()
    var result := SCORE.compute({
        "drops": drops_done,
        "contacts": contacts,
        "pathL": path_len_l,
        "pathR": path_len_r,
        "cfg": config
    })
    result["replay_scene"] = scene_file_path
    result["drill_id"] = GameState.current_drill
    result["target_drops"] = config.target_drops
    Telemetry.end_session(result)
    GameState.finish_drill(result)
