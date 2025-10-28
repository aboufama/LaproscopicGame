"""Game entities for LapDrop."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from math import cos, sin
from typing import Iterable, Optional

import pygame

Vec2 = pygame.math.Vector2


class BeadState(Enum):
    SPAWNED = auto()
    FALLING = auto()
    GRASPED = auto()
    DROPPED = auto()
    SCORED = auto()
    LOST = auto()


@dataclass(slots=True)
class Instrument:
    name: str
    tip: Vec2
    color: pygame.Color
    grasp_key: int
    move_keys: dict[str, int]
    fulcrum_inverted: bool = True
    grasped_bead: Optional["Bead"] = None
    path_length: float = 0.0
    _previous_tip: Vec2 = Vec2()

    def __post_init__(self) -> None:
        self._previous_tip = self.tip.copy()

    def update(self, pressed: Iterable[bool], dt: float, bounds_radius: float, speed: float) -> None:
        direction = Vec2(0, 0)
        if pressed[self.move_keys["up"]]:
            direction.y -= 1
        if pressed[self.move_keys["down"]]:
            direction.y += 1
        if pressed[self.move_keys["left"]]:
            direction.x -= 1
        if pressed[self.move_keys["right"]]:
            direction.x += 1

        if self.fulcrum_inverted:
            direction.x *= -1

        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.tip += direction * speed * dt

        if self.tip.length() > bounds_radius:
            self.tip.scale_to_length(bounds_radius)

        self.path_length += (self.tip - self._previous_tip).length()
        self._previous_tip = self.tip.copy()

    def grasp(self, bead: "Bead") -> None:
        self.grasped_bead = bead
        bead.state = BeadState.GRASPED
        bead.holder = self

    def release(self) -> None:
        if self.grasped_bead:
            bead = self.grasped_bead
            bead.state = BeadState.DROPPED
            bead.holder = None
            bead.velocity = Vec2(0, 0)
        self.grasped_bead = None


@dataclass(slots=True)
class Bead:
    position: Vec2
    radius: float = 8.0
    state: BeadState = BeadState.SPAWNED
    velocity: Vec2 = Vec2(0, 0)
    holder: Optional[Instrument] = None

    def update(self, dt: float, gravity: float, bounds_radius: float) -> None:
        if self.state == BeadState.GRASPED and self.holder:
            self.position = self.holder.tip.copy()
            self.velocity = Vec2(0, 0)
        elif self.state in {BeadState.SPAWNED, BeadState.FALLING, BeadState.DROPPED}:
            self.state = BeadState.FALLING
            self.velocity.y += gravity * dt
            self.position += self.velocity * dt
            if self.position.length() > bounds_radius + 80:
                self.state = BeadState.LOST

    def draw(self, surface: pygame.Surface, origin: Vec2) -> None:
        screen_pos = origin + self.position
        point = (int(screen_pos.x), int(screen_pos.y))
        pygame.draw.circle(surface, pygame.Color("#9cd6ff"), point, int(self.radius))
        pygame.draw.circle(surface, pygame.Color("white"), point, int(self.radius), 2)


@dataclass(slots=True)
class Aperture:
    id: str
    center: Vec2
    radius: float
    motion: Optional[dict[str, float]] = None
    _angle: float = 0.0

    def update(self, dt: float) -> None:
        if not self.motion:
            return
        if self.motion.get("kind") == "orbit":
            self._angle += self.motion.get("angular_speed", 0.0) * dt
            cx = self.motion.get("cx", 0.0)
            cy = self.motion.get("cy", 0.0)
            path_radius = self.motion.get("path_radius", 0.0)
            phase = self.motion.get("phase", 0.0)
            self.center.x = cx + path_radius * cos(self._angle + phase)
            self.center.y = cy + path_radius * sin(self._angle + phase)

    def draw(self, surface: pygame.Surface, origin: Vec2) -> None:
        screen_pos = origin + self.center
        point = (int(screen_pos.x), int(screen_pos.y))
        pygame.draw.circle(surface, pygame.Color("#00d8ff"), point, int(self.radius), 3)

    def contains(self, point: Vec2) -> bool:
        return point.distance_to(self.center) <= self.radius


@dataclass(slots=True)
class TissueZone:
    id: str
    center: Vec2
    size: Vec2
    penalty: float

    def draw(self, surface: pygame.Surface, origin: Vec2) -> None:
        rect = pygame.Rect(0, 0, int(self.size.x), int(self.size.y))
        rect.center = (int(origin.x + self.center.x), int(origin.y + self.center.y))
        color = pygame.Color(200, 50, 50, 120)
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        overlay.fill(color)
        surface.blit(overlay, rect)
        pygame.draw.rect(surface, pygame.Color("#ff4d4d"), rect, 2)

    def contains(self, point: Vec2) -> bool:
        dx = abs(point.x - self.center.x)
        dy = abs(point.y - self.center.y)
        return dx <= self.size.x / 2 and dy <= self.size.y / 2


def build_instrument(
    name: str,
    color: str,
    tip: tuple[float, float],
    move_keys: dict[str, int],
    grasp_key: int,
    fulcrum_inverted: bool = True,
) -> Instrument:
    return Instrument(
        name=name,
        tip=Vec2(tip),
        color=pygame.Color(color),
        move_keys=move_keys,
        grasp_key=grasp_key,
        fulcrum_inverted=fulcrum_inverted,
    )
