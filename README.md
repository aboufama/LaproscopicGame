# LapDrop: Stealth Surgeon

LapDrop: Stealth Surgeon is being rebuilt as a Python arcade-simulation experience inspired by laparoscopic training drills.
This repository now hosts the design documentation and Python-oriented project layout that will guide future implementation.

## Project Contents

- `docs/` – High-level design documentation for the Codex-assisted Python implementation.
- `src/` – Placeholder package structure where the Python gameplay systems will be implemented.
- `config/` – Example drill configuration directory.

## Next Steps

1. Use the design brief in `docs/LapDrop_Stealth_Surgeon_Design.md` to generate Python code (e.g., with Codex or manual development).
2. Implement the gameplay systems within the `src/lapdrop/` package following the modular architecture described in the document.
3. Add drill configuration files under `config/` to describe session parameters.
4. Record telemetry output to a `telemetry/` folder once runtime systems exist.

## Requirements

The future Python project is expected to rely on lightweight 2D frameworks such as **Pygame**, **Pyglet**, or **Arcade**. Declare concrete dependencies in `pyproject.toml` or `requirements.txt` as the implementation progresses.

## License

Add an explicit license once the project code is implemented.
