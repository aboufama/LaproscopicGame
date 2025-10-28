extends Node
class_name Easing

static func smoothstep(x: float) -> float:
    return x * x * (3.0 - 2.0 * x)

static func lerp(a, b, weight: float):
    return a + (b - a) * weight
