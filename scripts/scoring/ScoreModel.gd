extends Node

static var _penalty_bucket := 0

static func streak_multiplier(streak: int, sc: Dictionary) -> float:
    var per3 := sc.get("streak_per3", 0.05)
    var cap := sc.get("streak_cap", 1.5)
    return min(1.0 + (streak / 3) * per3, cap)

static func apply_penalty(kind: String, cfg) -> void:
    _penalty_bucket += int(cfg.penalties.get(kind, 0))

static func compute(payload: Dictionary) -> Dictionary:
    var drops: int = payload.get("drops", 0)
    var contacts: int = payload.get("contacts", 0)
    var path_total := payload.get("pathL", 0.0) + payload.get("pathR", 0.0)
    var cfg = payload.get("cfg")
    var optimal := max(1.0, float(drops) * 120.0)
    var economy := clamp(1.0 - path_total / optimal, 0.0, 1.0)
    var econ_weight := float(cfg.scoring.get("economy_weight", 0.25))
    var base := int(drops * 100 - contacts * 5 - _penalty_bucket)
    var score := max(0, int(base + economy * econ_weight * 1000.0))
    var grade := "C"
    if score >= 900:
        grade = "S"
    elif score >= 800:
        grade = "A"
    elif score >= 650:
        grade = "B"
    _penalty_bucket = 0
    return {
        "score": score,
        "grade": grade,
        "economy": economy,
        "drops": drops,
        "contacts": contacts
    }
