"""LapDrop: Stealth Surgeon game package."""
from __future__ import annotations

from .app import LapDropGame, run

__all__ = ["LapDropGame", "run", "main"]


def main() -> None:
    """Entry-point used by the ``lapdrop`` console script."""

    run()


if __name__ == "__main__":  # pragma: no cover - manual invocation
    run()
