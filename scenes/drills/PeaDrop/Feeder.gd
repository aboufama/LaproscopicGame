extends Node2D

var config: DrillConfig
var elapsed := 0.0
var timer := 0.0
var next_interval := 2.0

func setup(cfg: DrillConfig) -> void:
    config = cfg
    elapsed = 0.0
    timer = 0.0
    next_interval = cfg.feeder_start_interval

func advance(delta: float) -> bool:
    if config == null:
        return false
    elapsed += delta
    timer += delta
    if timer >= next_interval:
        timer = 0.0
        var alpha := clamp(elapsed / max(config.duration_s, 0.1), 0.0, 1.0)
        if config.interval_curve:
            alpha = config.interval_curve.sample(alpha)
        next_interval = lerp(config.feeder_start_interval, config.feeder_end_interval, alpha)
        return true
    return false

func spawn_position() -> Vector2:
    return global_position
