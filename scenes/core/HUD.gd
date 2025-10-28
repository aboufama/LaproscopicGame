extends CanvasLayer

@onready var timer_label := $TimerLabel
@onready var drops_label := $DropsLabel
@onready var streak_bar := $Streak/Progress
@onready var pulse_rect := $PulseRect
@onready var results_panel := $Results

func enter_drill(_drill) -> void:
    visible = true
    results_panel.visible = false
    reset()

func exit_drill() -> void:
    reset()
    visible = false

func set_hud(_drill) -> void:
    pass

func reset() -> void:
    update_timer(0.0)
    update_drops(0, 0)
    bump_streak(0, 1.0)
    pulse_rect.modulate.a = 0.0

func update_timer(time_left: float) -> void:
    timer_label.text = str(roundf(max(time_left, 0.0)))

func update_drops(done: int, target: int) -> void:
    drops_label.text = "%d/%d" % [done, target]

func bump_streak(streak: int, mult: float) -> void:
    streak_bar.value = clamp(streak * 10, 0, 100)
    streak_bar.tooltip_text = "x%.2f" % mult

func flash_error() -> void:
    pulse_rect.modulate.a = 0.75
    var tween := create_tween()
    tween.tween_property(pulse_rect, "modulate:a", 0.0, 0.2)

func show_results(result: Dictionary) -> void:
    visible = true
    results_panel.visible = true
    results_panel.get_node("VBoxContainer/Score").text = "Score: %d" % result.get("score", 0)
    results_panel.get_node("VBoxContainer/Grade").text = "Grade: %s" % result.get("grade", "-")
    results_panel.get_node("VBoxContainer/Economy").text = "Economy: %.2f" % result.get("economy", 0.0)

func on_retry_pressed() -> void:
    if GameState.last_result.has("replay_scene"):
        var scene_path: String = GameState.last_result.get("replay_scene", "")
        var drill_id: String = GameState.last_result.get("drill_id", "")
        if drill_id != "":
            GameState.start_drill(drill_id, scene_path)
        else:
            GameState.goto_scene(scene_path)

func on_menu_pressed() -> void:
    GameState.goto_scene("res://ui/Menus/DrillSelect.tscn")
