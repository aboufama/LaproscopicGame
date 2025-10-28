extends Node

var players: Dictionary = {}

func _ready() -> void:
    players["buzz"] = _make_player()
    players["perfect"] = _make_player()
    players["drop"] = _make_player()

func buzz() -> void:
    _play("buzz")

func perfect() -> void:
    _play("perfect")

func drop() -> void:
    _play("drop")

func _make_player() -> AudioStreamPlayer:
    var player := AudioStreamPlayer.new()
    add_child(player)
    return player

func _play(name: String) -> void:
    var player: AudioStreamPlayer = players.get(name)
    if player:
        player.stop()
        player.play()
