# LapDrop: Stealth Surgeon

LapDrop: Stealth Surgeon is a laparoscopic training-inspired arcade simulation written in Python
using [Pygame](https://www.pygame.org/). Guide two articulated laparoscopic instruments, capture
falling beads, and drop them cleanly through endoscopic apertures while avoiding tissue hazards.

[Design brief](docs/LapDrop_Stealth_Surgeon_Design.md)

## Features

- Modular Python implementation of the design brief, including instruments, beads, apertures,
  tissue hazards, scoring, telemetry, and configurable drills.
- JSON-driven drill definitions; the included **Pea Drop Plus** session demonstrates static and
  orbiting apertures with progressive bead spawn timing.
- Fully interactive training loop with scoring breakdowns, streaks, and telemetry logging to
  NDJSON for later analysis.

## Getting Started

### 1. Install Dependencies

This project targets Python 3.11 or newer. Install the runtime requirements with `pip`:

```bash
pip install -e .
```

### 2. Run the Game

Start the default Pea Drop Plus drill:

```bash
lapdrop
```

To run a custom drill configuration, pass the JSON path:

```bash
python -m lapdrop.app path/to/custom_drill.json
```

### 3. Controls

| Action                     | Left Instrument | Right Instrument |
| -------------------------- | --------------- | ---------------- |
| Move instrument            | `WASD`          | Arrow keys       |
| Grasp / release bead       | `F`             | `J`              |
| Pause / exit application   | `Esc`           | `Esc`            |

Both instruments simulate fulcrum inversion—horizontal motion is mirrored around the viewport
center, mimicking laparoscopic tool mechanics.

### Telemetry

Telemetry logs are written to `telemetry/` as newline-delimited JSON files when a session ends. Each
record captures timestamped events such as bead spawns, grasps, tissue contacts, and the final
score. The logs can be analyzed with standard JSON tooling.

### Configuration

Drills are described in JSON. See `config/drills/pea_drop_plus.json` for an example. Each drill
specifies duration, spawn intervals, apertures (static or orbiting), tissue hazard shapes, and
scoring modifiers. Additional drills can be added by dropping new JSON files into `config/drills/`
and launching the game with their paths.

## Development

The core modules live under `src/lapdrop/`:

- `app.py` – the main loop, state machine, rendering, and HUD.
- `config.py` – JSON parsing into strongly typed drill configurations.
- `entities.py` – gameplay objects (instruments, beads, apertures, tissue).
- `feeder.py` – bead spawning cadence logic.
- `scoring.py` – scoring aggregation and grade calculation.
- `telemetry.py` – NDJSON telemetry recording utilities.

Refer to `docs/LapDrop_Stealth_Surgeon_Design.md` for the full design brief and future expansion
ideas.

## License

An explicit license will be added in a future update.
