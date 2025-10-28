# LapDrop: Stealth Surgeon

LapDrop is a Godot 4 project that prototypes the Pea Drop+ laparoscopic timing drill. It scaffolds the full training flow with reusable systems for drills, scoring, and telemetry so new exercises can be added quickly.

## Getting Started

1. [Install Godot 4.2](https://godotengine.org/download). The project targets the OpenGL renderer for broad compatibility.
2. Clone this repository and open `project.godot` from the Godot project manager.
3. Press <kbd>F5</kbd> to launch the game. Use a gamepad or the keyboard mappings listed below.

## Controls

| Action | Gamepad | Keyboard |
| --- | --- | --- |
| Move left instrument | Left stick | W/A/S/D |
| Move right instrument | Right stick | I/J/K/L |
| Grip left instrument | LT | F |
| Grip right instrument | RT | J |
| Swap instruments | A | Tab |
| Zoom camera in/out | Right trigger axis | Q / E or Mouse Wheel |
| Pause | Start | Esc |

## Repository Structure

```
res://
├── autoload/             # GameState, telemetry, SFX, and runtime config singletons
├── scenes/
│   ├── core/             # Main scene and HUD
│   ├── drills/PeaDrop/   # Pea Drop+ drill scenes and scripts
│   ├── instruments/      # Instrument rigs and controllers
│   └── anatomy/          # Tissue collision proxies
├── scripts/              # Shared resources and scoring helpers
├── data/drills/          # DrillConfig resources
├── ui/Menus/             # Title and drill select screens
└── audio/, art/, etc.    # Placeholders for future assets
```

## Current Features

- **Pea Drop+ Drill:** Feeder-driven bead spawns, moving apertures, and tissue collision penalties.
- **Laparoscope Rig:** Dual-instrument controller with fulcrum inversion and tremor settings.
- **Scoring & Telemetry:** Streak multiplier, economy estimate, and NDJSON session logs written to `user://`.
- **Reusable HUD:** Timer, drop counter, streak meter, and results overlay with retry routing.

## Adding New Drills

1. Create a new `DrillConfig` resource in `data/drills/` for spawn cadence, apertures, and penalties.
2. Duplicate `scenes/drills/PeaDrop/PeaDrop.tscn` as a starting point and swap in drill-specific controllers.
3. Register the drill in `ui/Menus/DrillSelect.gd` to expose it in the menu.

## Telemetry Files

Session logs are exported to the Godot `user://` directory (platform-specific). Each session creates a `<drill>_<timestamp>.ndjson` file that contains per-event records suitable for analytics pipelines.

---

The project is intentionally light on final art and audio so designers can iterate on feel and telemetry before polishing the presentation.
