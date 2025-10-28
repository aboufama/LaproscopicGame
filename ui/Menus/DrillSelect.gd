extends Control

var drills := [
    {
        "id": "pea_drop",
        "title": "Pea Drop+",
        "scene": "res://scenes/drills/PeaDrop/PeaDrop.tscn"
    }
]

func _ready() -> void:
    _populate()

func _populate() -> void:
    var list := $MarginContainer/VBoxContainer/DrillList
    list.clear()
    for drill in drills:
        var item := drill["title"]
        list.add_item(item)

func _on_drill_selected(index: int) -> void:
    if index < 0 or index >= drills.size():
        return
    var drill := drills[index]
    GameState.start_drill(drill["id"], drill["scene"])

func _on_back_pressed() -> void:
    GameState.goto_scene("res://ui/Menus/Title.tscn")
