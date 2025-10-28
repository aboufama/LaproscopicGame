"""Scoring helpers for LapDrop."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ScoreBreakdown:
    drops: int = 0
    misses: int = 0
    tissue_contacts: int = 0
    streak: int = 0
    best_streak: int = 0
    score: float = 0.0
    economy_distance: float = 0.0
    perfect_drops: int = 0

    def register_drop(self, perfect_bonus: float = 0.0) -> None:
        self.drops += 1
        self.streak += 1
        self.best_streak = max(self.best_streak, self.streak)
        self.score += 100 + perfect_bonus
        self.perfect_drops += 1 if perfect_bonus > 0 else 0

    def register_miss(self, penalty: float) -> None:
        self.misses += 1
        self.streak = 0
        self.score -= penalty

    def register_tissue_contact(self, penalty: float) -> None:
        self.tissue_contacts += 1
        self.streak = 0
        self.score -= penalty

    def finalize(self, economy_weight: float, target_distance: float) -> None:
        if target_distance <= 0:
            return
        efficiency = max(0.0, 1.0 - (self.economy_distance / target_distance))
        self.score += efficiency * economy_weight

    def grade(self) -> str:
        thresholds = [(900, "S"), (750, "A"), (600, "B"), (450, "C"), (0, "D")]
        for threshold, letter in thresholds:
            if self.score >= threshold:
                return letter
        return "D"
