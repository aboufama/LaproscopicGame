"""Bead feeder logic."""
from __future__ import annotations

from dataclasses import dataclass

import pygame

from .entities import Bead

Vec2 = pygame.math.Vector2


@dataclass(slots=True)
class BeadFeeder:
    spawn_interval_start: float
    spawn_interval_end: float
    duration: float
    elapsed: float = 0.0
    time_since_spawn: float = 0.0

    def update(self, dt: float) -> None:
        self.elapsed += dt
        self.time_since_spawn += dt

    def should_spawn(self) -> bool:
        return self.time_since_spawn >= self.current_interval

    def spawn(self, position: Vec2) -> Bead:
        self.time_since_spawn = 0.0
        return Bead(position=position.copy())

    @property
    def current_interval(self) -> float:
        progress = 0.0
        if self.duration > 0:
            progress = min(1.0, self.elapsed / self.duration)
        return self.spawn_interval_start + (
            self.spawn_interval_end - self.spawn_interval_start
        ) * progress
