"""Telemetry logging for LapDrop sessions."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
import json


@dataclass(slots=True)
class TelemetryEvent:
    timestamp: float
    event: str
    payload: dict[str, Any]


class TelemetryLogger:
    """Collects telemetry events and emits them to a NDJSON file at session end."""

    def __init__(self, drill_id: str, output_dir: Path) -> None:
        self.drill_id = drill_id
        self.output_dir = output_dir
        self.events: list[TelemetryEvent] = []
        self.start_time = datetime.utcnow()

    def record(self, timestamp: float, event: str, **payload: Any) -> None:
        self.events.append(TelemetryEvent(timestamp, event, payload))

    def extend(self, events: Iterable[TelemetryEvent]) -> None:
        self.events.extend(events)

    def flush(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        filename = (
            f"telemetry_{self.drill_id}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.ndjson"
        )
        path = self.output_dir / filename
        with path.open("w", encoding="utf-8") as fh:
            for event in self.events:
                fh.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
        return path
