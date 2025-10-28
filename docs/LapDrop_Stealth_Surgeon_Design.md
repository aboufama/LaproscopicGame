# LapDrop: Stealth Surgeon — Python Game Design Document (for Codex)

## General Overview

LapDrop: Stealth Surgeon is a **Python arcade-simulation game** inspired by laparoscopic training tasks.
The player controls two surgical instruments through a constrained circular viewport and must perform **timed bead drops** into target apertures while avoiding “tissue” collisions.
The objective is to train fine motor coordination, bimanual control, and precision timing through a fast, repeatable skill loop.

The game should run using a lightweight 2D Python framework such as **Pygame**, **Pyglet**, or **Arcade**.
All visuals are simple shapes and outlines: instruments are slender rods, beads are small circles, apertures are hollow rings, and tissue zones are colored hazard regions.
The game emphasizes **smooth motion, accurate collision logic, responsive timing, and juicy feedback** over photorealism.

## Core Gameplay Loop

1. The player is briefed on the upcoming drill: target count, drop rhythm, hazards.
2. A timed session (typically 60 seconds) begins.
3. Beads spawn periodically from a feeder and fall into the player’s workspace.
4. The player must catch a bead with one instrument, optionally transfer it to the other, and drop it through a circular aperture.
5. Touching tissue areas or missing the aperture reduces the score.
6. The session ends when the timer expires or the target number of drops is completed.
7. A results screen displays accuracy, speed, economy of motion, and a letter grade.

## Learning Objectives

- Reinforce control of **both hands independently**.
- Simulate **fulcrum inversion** (movement reverses around a pivot point).
- Encourage **minimal, efficient motion paths**.
- Train reaction to increasing speed (shorter bead spawn intervals).
- Develop rhythm and hand-eye coordination under pressure.

## Visual & Aesthetic Direction

The art style is **clean and minimal**, with medical-sci-fi colors: deep blue backgrounds, white tools, neon blue apertures, and red “no-touch” zones.
Particles or glow effects appear on perfect drops, and a red vignette pulse occurs when contact is made with a forbidden area.
The circular endoscopic mask defines the playfield boundaries.

## Controls

- **Left instrument:** WASD or left stick
- **Right instrument:** Arrow keys or right stick
- **Grasp/Release:** F for left, J for right
- **Swap active hand:** Spacebar
- **Pause/Menu:** Esc

Both instruments can move independently. Movement may be mirrored horizontally to simulate the laparoscopic fulcrum effect.

## Game Structure

The project should be modular and divided into these systems:

### 1. Core Loop

Manages state transitions: menu → briefing → drill → results.
Handles global timing, frame updates, and telemetry logging.

### 2. Instruments

Two controllable rods each with:

- Position and velocity
- Grasp state (open/closed)
- Fulcrum inversion logic (horizontal mirroring)
- Collision detection with beads and tissue
- Optional attached bead reference when grasped

### 3. Beads

Each bead object has:

- Position, velocity, and gravity
- State machine: SPAWNED → FALLING → GRASPED → DROPPED → SCORED or LOST
- Behavior when grasped (follows instrument tip)
- Collision with apertures and tissue

### 4. Apertures

Circular targets that can be static or moving.
If a bead is dropped inside the radius without touching walls, it counts as a successful drop.
The game can later add rotating or shrinking apertures for higher difficulty.

### 5. Tissue Zones

Static or moving hazard regions.
If a bead or instrument touches them, a penalty is applied and a warning effect is triggered.

### 6. Feeder System

Controls bead spawn timing.
Spawn interval decreases gradually during the session to increase difficulty.
Example: start at 2.0 seconds per bead and reduce to 1.0 second linearly over 60 seconds.

### 7. Scoring System

Tracks:

- Successful drops
- Misses and tissue contacts
- Streaks of perfect drops
- Path length or efficiency metric

Final score combines:

- Time efficiency
- Accuracy
- Economy of motion (shorter travel paths)
- Penalties (contact, misses, late catches)

Grades: S, A, B, C based on percentile thresholds.

### 8. HUD and UI

On-screen timer, score counter, streak meter, and warning indicators.
Menus for selecting drills and viewing results.
Results screen shows numeric breakdown and letter grade.

### 9. Telemetry System

Logs session data for later analysis.
Each frame or major event (spawn, grasp, drop, contact) is stored as a JSON or NDJSON line.
Each record includes timestamps, instrument positions, bead state, and events.
At session end, data is saved to a file like `telemetry_pea_drop_2025.ndjson`.

### 10. Configuration

Each drill is described by a JSON or YAML file defining:

- Duration and target count
- Spawn interval start and end
- Aperture positions and movement
- Penalty weights
- Scoring parameters

This allows easy addition of new drills without modifying core code.

## Example Drills

### Pea Drop Plus (Signature Drill)

- Duration: 60 seconds
- Two apertures: one fixed, one slowly moving in a circular path
- Beads spawn every 2→1 seconds over time
- Goal: 12 successful drops
- Penalty for missed or lost bead: −8 points
- Tissue contact: −5 points
- Moving aperture grants bonus on perfect timing

### Cylinder Transfer

- No falling beads. Cylinders rest on pegs.
- Player must pick up each cylinder and move it to another peg without touching sides.
- Tests coordination and depth control.

### Cobra Rope

- Flexible rope or chain of linked nodes.
- Player must drag the rope along a narrow path without touching forbidden zones.
- Trains smooth continuous motion.

### Terrible Triangle

- Needle simulation. Player inserts through rings along a triangular path.
- Contact with edges penalized.
- Teaches controlled depth and trajectory.

## Data Flow & Logic Summary

1. Load drill configuration file.
2. Initialize instrument, aperture, feeder, and environment objects.
3. Start global timer and spawn first bead.
4. Each frame:
   - Read player input → update instrument positions.
   - Update bead positions, check collisions.
   - If bead dropped inside aperture → add score.
   - If bead leaves screen or touches tissue → penalty.
   - Log telemetry events.
5. When timer reaches zero, compute final score and display results.
6. Save telemetry and reset for next session.

## Scoring Formula (Conceptual)

```
score = (drops * 100)
       - (tissue_contacts * penalty_touch)
       - (misses * penalty_miss)
       + (economy_weight * economy_score)
       + (streak_bonus)
```

Economy score is calculated from total instrument travel length compared to an optimal baseline.
Streak bonus increases every 3 perfect drops up to a cap.

## Game Feel and Feedback

- Perfect drop → bright particle burst + chime
- Tissue contact → red flash, buzz sound
- Miss → dull bounce sound
- Streak meter pulses as multiplier increases
- Dynamic background lighting that brightens with player performance

## Audio

- Gentle background hum resembling operating room equipment
- Metronome tick in rhythm with bead spawn interval
- Positive feedback tones for precision
- Brief buzz for penalties

## Performance Targets

- 60 FPS on typical laptop hardware
- Input latency < 30 ms
- Physics updates independent of frame rate
- Telemetry logging under 1 MB per session

## Extensibility

The design allows new drills to be added simply by adding configuration files and new scene modules.
All objects (beads, apertures, tissue) follow a standard interface for update, draw, and collision detection.

Future extensions:

- Ghost replays (visualizing best run)
- Multiplayer or split-screen competition mode
- Adaptive difficulty scaling based on performance
- Integration with real laparoscopic hardware or haptic controllers

## Summary for Codex

Codex should:

1. Generate a modular Python project structure as described above.
2. Use object-oriented design (classes for Game, Instrument, Bead, Aperture, etc.).
3. Include a main loop managing timing, input, and updates.
4. Implement JSON-based configuration and telemetry output.
5. Provide clean visual feedback with minimal assets.
6. Focus on precision, timing, and fun feedback rather than realism.

---

**End of design document.**
