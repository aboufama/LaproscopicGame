extends Node

var session_meta: Dictionary = {}
var lines: Array[String] = []

func begin_session(drill_id: String, title: String) -> void:
    session_meta = {
        "drill": drill_id,
        "title": title,
        "start": Time.get_unix_time_from_system()
    }
    _push({"evt": "start", "drill": drill_id, "title": title})

func log_event(payload: Dictionary) -> void:
    _push(payload)

func end_session(summary: Dictionary) -> void:
    _push({"evt": "end"} | summary)
    _flush(summary)
    session_meta.clear()

func _push(payload: Dictionary) -> void:
    var enriched := payload.duplicate(true)
    enriched["t"] = Time.get_ticks_msec() / 1000.0
    lines.append(JSON.stringify(enriched))

func _flush(summary: Dictionary) -> void:
    var ts := int(Time.get_unix_time_from_system())
    var drill_id := session_meta.get("drill", "unknown")
    var filename := "user://%s_%d.ndjson" % [drill_id, ts]
    var file := FileAccess.open(filename, FileAccess.WRITE)
    for line in lines:
        file.store_line(line)
    file.close()
    lines.clear()
