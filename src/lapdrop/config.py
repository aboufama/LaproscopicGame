"""Loading and data structures for LapDrop drill configurations."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, List, Sequence
import json


@dataclass(slots=True)
class SpawnInterval:
    """Time interval between bead spawns at the start and end of the drill."""

    start: float
    end: float

    def at_progress(self, progress: float) -> float:
        """Return a spawn interval interpolated by ``progress`` (0..1)."""

        progress = max(0.0, min(1.0, progress))
        return self.start + (self.end - self.start) * progress


@dataclass(slots=True)
class ApertureMotion:
    """Optional motion profile for an aperture."""

    kind: str
    params: dict[str, float]


@dataclass(slots=True)
class ApertureConfig:
    id: str
    position: Sequence[float]
    radius: float
    motion: ApertureMotion | None = None


@dataclass(slots=True)
class TissueZoneConfig:
    id: str
    center: Sequence[float]
    size: Sequence[float]
    penalty: float


@dataclass(slots=True)
class DrillConfig:
    id: str
    name: str
    duration_seconds: float
    target_drops: int
    spawn_interval: SpawnInterval
    apertures: List[ApertureConfig] = field(default_factory=list)
    tissue_zones: List[TissueZoneConfig] = field(default_factory=list)
    penalties: dict[str, float] = field(default_factory=dict)
    bonuses: dict[str, float] = field(default_factory=dict)


class ConfigError(RuntimeError):
    """Raised when a configuration file cannot be parsed."""


def _require(sequence: Iterable[str], data: dict[str, Any]) -> None:
    for key in sequence:
        if key not in data:
            raise ConfigError(f"Missing required key '{key}' in drill definition")


def _load_apertures(items: Sequence[dict[str, Any]]) -> List[ApertureConfig]:
    apertures: List[ApertureConfig] = []
    for entry in items:
        _require(["id", "radius"], entry)
        motion: ApertureMotion | None = None
        position: Sequence[float]

        if entry.get("type", "static") == "orbit":
            _require(["center", "path_radius", "angular_speed"], entry)
            motion = ApertureMotion(
                kind="orbit",
                params={
                    "cx": float(entry["center"][0]),
                    "cy": float(entry["center"][1]),
                    "path_radius": float(entry["path_radius"]),
                    "angular_speed": float(entry["angular_speed"]),
                    "phase": float(entry.get("phase", 0.0)),
                },
            )
            position = tuple(entry["center"])
        else:
            _require(["position"], entry)
            position = tuple(entry["position"])

        apertures.append(
            ApertureConfig(
                id=str(entry["id"]),
                position=tuple(float(v) for v in position),
                radius=float(entry["radius"]),
                motion=motion,
            )
        )
    return apertures


def _load_tissue(items: Sequence[dict[str, Any]]) -> List[TissueZoneConfig]:
    tissue: List[TissueZoneConfig] = []
    for entry in items:
        if entry.get("shape", "rectangle") != "rectangle":
            raise ConfigError(f"Unsupported tissue shape: {entry.get('shape')} (only rectangle)")
        _require(["id", "center", "size", "penalty"], entry)
        tissue.append(
            TissueZoneConfig(
                id=str(entry["id"]),
                center=tuple(float(v) for v in entry["center"]),
                size=tuple(float(v) for v in entry["size"]),
                penalty=float(entry["penalty"]),
            )
        )
    return tissue


def load_drill_config(path: str | Path) -> DrillConfig:
    """Load a drill configuration from JSON."""

    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:  # pragma: no cover - user environment specific
        raise ConfigError(f"Failed to read drill config {path!s}: {exc}") from exc
    except json.JSONDecodeError as exc:  # pragma: no cover - user environment specific
        raise ConfigError(f"Invalid JSON in {path!s}: {exc}") from exc

    _require(["id", "name", "duration_seconds", "target_drops", "spawn_interval"], data)
    spawn_data = data["spawn_interval"]
    _require(["start", "end"], spawn_data)

    apertures = _load_apertures(data.get("apertures", []))
    tissue = _load_tissue(data.get("tissue_zones", []))

    return DrillConfig(
        id=str(data["id"]),
        name=str(data["name"]),
        duration_seconds=float(data["duration_seconds"]),
        target_drops=int(data["target_drops"]),
        spawn_interval=SpawnInterval(
            start=float(spawn_data["start"]),
            end=float(spawn_data["end"]),
        ),
        apertures=apertures,
        tissue_zones=tissue,
        penalties={k: float(v) for k, v in data.get("penalties", {}).items()},
        bonuses={k: float(v) for k, v in data.get("bonuses", {}).items()},
    )


def default_drill_path() -> Path:
    """Return the default drill configuration location bundled with the project."""

    project_root = Path(__file__).resolve().parents[2]
    return project_root / "config" / "drills" / "pea_drop_plus.json"
