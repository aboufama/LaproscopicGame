extends Node

var settings := {
    "fulcrum_inversion": true,
    "tremor_amp": 0.0,
    "aperture_scale": 1.0
}

signal setting_changed(name: String, value)

func get_setting(name: String, default_value = null):
    return settings.get(name, default_value)

func set_setting(name: String, value) -> void:
    settings[name] = value
    emit_signal("setting_changed", name, value)
