"""Main application loop for LapDrop."""
from __future__ import annotations

import argparse

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

import pygame

from .config import DrillConfig, default_drill_path, load_drill_config
from .entities import (
    Aperture,
    Bead,
    BeadState,
    Instrument,
    TissueZone,
    Vec2,
    build_instrument,
)
from .feeder import BeadFeeder
from .scoring import ScoreBreakdown
from .telemetry import TelemetryLogger

WINDOW_SIZE = (1200, 800)
WORKSPACE_RADIUS = 260
INSTRUMENT_SPEED = 260.0
GRAVITY = 540.0
ECONOMY_WEIGHT = 250.0
ECONOMY_BASELINE_PER_DROP = 120.0
BEAD_GRASP_DISTANCE = 24.0


class GameMode(Enum):
    TITLE = auto()
    RUNNING = auto()
    RESULTS = auto()


@dataclass(slots=True)
class SessionResult:
    breakdown: ScoreBreakdown
    duration_played: float
    telemetry_path: Path


class LapDropGame:
    def __init__(self, drill_path: str | Path | None = None) -> None:
        self.drill_path = Path(drill_path) if drill_path else default_drill_path()
        self.config: DrillConfig = load_drill_config(self.drill_path)
        self.mode = GameMode.TITLE
        self.screen: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None
        self.font_small: pygame.font.Font | None = None
        self.font_large: pygame.font.Font | None = None
        self.origin = Vec2(0, 0)
        self.background = pygame.Color("#041833")
        self.workspace_color = pygame.Color("#073b65")
        self.telemetry_logger: TelemetryLogger | None = None
        self.session_result: SessionResult | None = None

        self.left_instrument: Instrument | None = None
        self.right_instrument: Instrument | None = None
        self.instruments: list[Instrument] = []
        self.apertures: list[Aperture] = []
        self.tissue_zones: list[TissueZone] = []
        self.beads: list[Bead] = []
        self.feeder: BeadFeeder | None = None
        self.score = ScoreBreakdown()
        self.elapsed_time = 0.0
        self.contact_flags: dict[tuple[str, str], bool] = {}
        self.bead_contact_flags: dict[tuple[str, int], bool] = {}
        self.flash_timer = 0.0

    def setup_pygame(self) -> None:
        pygame.init()
        pygame.display.set_caption("LapDrop: Stealth Surgeon")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont("Fira Sans", 20)
        self.font_large = pygame.font.SysFont("Fira Sans", 48, bold=True)
        self.origin = Vec2(self.screen.get_width() / 2, self.screen.get_height() / 2)

    def reset_session(self) -> None:
        self.score = ScoreBreakdown()
        self.elapsed_time = 0.0
        self.flash_timer = 0.0
        self.session_result = None
        self.telemetry_logger = TelemetryLogger(self.config.id, Path("telemetry"))
        self.beads = []
        self.apertures = self._build_apertures(self.config)
        self.tissue_zones = self._build_tissue(self.config)
        self.feeder = BeadFeeder(
            spawn_interval_start=self.config.spawn_interval.start,
            spawn_interval_end=self.config.spawn_interval.end,
            duration=self.config.duration_seconds,
        )
        self.left_instrument = build_instrument(
            name="Left",
            color="#f4f7ff",
            tip=(-120, 80),
            move_keys={
                "up": pygame.K_w,
                "down": pygame.K_s,
                "left": pygame.K_a,
                "right": pygame.K_d,
            },
            grasp_key=pygame.K_f,
            fulcrum_inverted=True,
        )
        self.right_instrument = build_instrument(
            name="Right",
            color="#c8e7ff",
            tip=(120, 80),
            move_keys={
                "up": pygame.K_UP,
                "down": pygame.K_DOWN,
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
            },
            grasp_key=pygame.K_j,
            fulcrum_inverted=True,
        )
        self.instruments = [self.left_instrument, self.right_instrument]
        self.contact_flags.clear()
        self.bead_contact_flags.clear()

    def run(self) -> None:
        if not pygame.get_init():
            self.setup_pygame()
        assert self.screen and self.clock and self.font_small and self.font_large

        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    self.handle_event(event)

            if not running:
                break

            self.update(dt)
            self.render()

        pygame.quit()

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.mode == GameMode.TITLE and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset_session()
                self.mode = GameMode.RUNNING
        elif self.mode == GameMode.RUNNING and event.type == pygame.KEYDOWN:
            for instrument in self.instruments:
                if event.key == instrument.grasp_key:
                    self._toggle_grasp(instrument)
        elif self.mode == GameMode.RESULTS and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.mode = GameMode.TITLE

    def update(self, dt: float) -> None:
        if self.mode == GameMode.RUNNING:
            self.update_running(dt)
        elif self.mode == GameMode.TITLE:
            self.flash_timer = (self.flash_timer + dt) % 1.5

    def update_running(self, dt: float) -> None:
        assert self.feeder and self.telemetry_logger

        self.elapsed_time += dt
        pressed = pygame.key.get_pressed()
        for instrument in self.instruments:
            instrument.update(pressed, dt, WORKSPACE_RADIUS, INSTRUMENT_SPEED)

        self.score.economy_distance = sum(inst.path_length for inst in self.instruments)

        for aperture in self.apertures:
            aperture.update(dt)

        self.feeder.update(dt)
        if self.feeder.should_spawn():
            bead = self.feeder.spawn(Vec2(0, -WORKSPACE_RADIUS + 30))
            bead.state = BeadState.FALLING
            self.beads.append(bead)
            self.telemetry_logger.record(self.elapsed_time, "spawn", position=list(bead.position))

        for bead in list(self.beads):
            previous_state = bead.state
            bead.update(dt, gravity=GRAVITY, bounds_radius=WORKSPACE_RADIUS)

            if bead.state == BeadState.FALLING:
                self._check_aperture_score(bead)

            if bead.state == BeadState.LOST and previous_state != BeadState.LOST:
                penalty = self.config.penalties.get("missed_drop", 8)
                self.score.register_miss(penalty)
                self.telemetry_logger.record(
                    self.elapsed_time,
                    "miss",
                    position=list(bead.position),
                    penalty=penalty,
                )
                self.beads.remove(bead)
                continue

            if bead.state == BeadState.SCORED and previous_state != BeadState.SCORED:
                self.beads.remove(bead)
                continue

            self._check_tissue_for_bead(bead)

        self._check_tissue_for_instruments()

        if self.flash_timer > 0:
            self.flash_timer = max(0.0, self.flash_timer - dt)

        if self.elapsed_time >= self.config.duration_seconds or self.score.drops >= self.config.target_drops:
            self.finish_session()
            return

    def _toggle_grasp(self, instrument: Instrument) -> None:
        if instrument.grasped_bead:
            instrument.release()
            if self.telemetry_logger:
                self.telemetry_logger.record(
                    self.elapsed_time, "release", instrument=instrument.name
                )
            return

        candidate = self._nearest_bead(instrument.tip)
        if candidate and candidate.position.distance_to(instrument.tip) <= BEAD_GRASP_DISTANCE:
            instrument.grasp(candidate)
            candidate.velocity = Vec2(0, 0)
            if self.telemetry_logger:
                self.telemetry_logger.record(
                    self.elapsed_time,
                    "grasp",
                    instrument=instrument.name,
                    bead_position=list(candidate.position),
                )

    def _nearest_bead(self, point: Vec2) -> Bead | None:
        available = [b for b in self.beads if b.state in {BeadState.FALLING, BeadState.SPAWNED}]
        if not available:
            return None
        return min(available, key=lambda bead: bead.position.distance_to(point))

    def _check_aperture_score(self, bead: Bead) -> None:
        for aperture in self.apertures:
            if aperture.contains(bead.position):
                bead.state = BeadState.SCORED
                perfect_bonus = self.config.bonuses.get("perfect_drop", 15.0)
                multiplier = 1.0
                if aperture.motion:
                    multiplier = self.config.bonuses.get("moving_target_multiplier", 1.0)
                self.score.register_drop(perfect_bonus * multiplier)
                if self.telemetry_logger:
                    self.telemetry_logger.record(
                        self.elapsed_time,
                        "score",
                        aperture=aperture.id,
                        multiplier=multiplier,
                        perfect_bonus=perfect_bonus,
                    )
                break

    def _check_tissue_for_instruments(self) -> None:
        penalty_base = self.config.penalties.get("tissue_contact", 5.0)
        for zone in self.tissue_zones:
            for instrument in self.instruments:
                key = (zone.id, instrument.name)
                touching = zone.contains(instrument.tip)
                previous = self.contact_flags.get(key, False)
                if touching and not previous:
                    self.contact_flags[key] = True
                    self.score.register_tissue_contact(penalty_base)
                    self.flash_timer = 0.3
                    if self.telemetry_logger:
                        self.telemetry_logger.record(
                            self.elapsed_time,
                            "tissue_contact",
                            zone=zone.id,
                            instrument=instrument.name,
                            penalty=penalty_base,
                        )
                elif not touching and previous:
                    self.contact_flags[key] = False

    def _check_tissue_for_bead(self, bead: Bead) -> None:
        penalty_base = self.config.penalties.get("tissue_contact", 5.0)
        for zone in self.tissue_zones:
            key = (zone.id, id(bead))
            touching = zone.contains(bead.position)
            previous = self.bead_contact_flags.get(key, False)
            if touching and not previous:
                self.bead_contact_flags[key] = True
                self.score.register_tissue_contact(penalty_base)
                self.flash_timer = 0.3
                if self.telemetry_logger:
                    self.telemetry_logger.record(
                        self.elapsed_time,
                        "tissue_contact",
                        zone=zone.id,
                        bead=True,
                        penalty=penalty_base,
                    )
            elif not touching and previous:
                self.bead_contact_flags[key] = False

    def finish_session(self) -> None:
        assert self.telemetry_logger
        self.score.finalize(
            economy_weight=ECONOMY_WEIGHT,
            target_distance=self.config.target_drops * ECONOMY_BASELINE_PER_DROP,
        )
        self.telemetry_logger.record(
            self.elapsed_time,
            "session_end",
            score=self.score.score,
            drops=self.score.drops,
            misses=self.score.misses,
            tissue_contacts=self.score.tissue_contacts,
        )
        telemetry_path = self.telemetry_logger.flush()
        self.session_result = SessionResult(
            breakdown=self.score,
            duration_played=self.elapsed_time,
            telemetry_path=telemetry_path,
        )
        for instrument in self.instruments:
            instrument.grasped_bead = None
        self.beads.clear()
        self.mode = GameMode.RESULTS

    def render(self) -> None:
        assert self.screen and self.font_small and self.font_large
        self.screen.fill(self.background)
        self._draw_workspace(self.screen)

        if self.mode == GameMode.TITLE:
            self._draw_title()
        elif self.mode == GameMode.RUNNING:
            self._draw_running()
        elif self.mode == GameMode.RESULTS:
            self._draw_results()

        pygame.display.flip()

    def _draw_workspace(self, surface: pygame.Surface) -> None:
        center = (int(self.origin.x), int(self.origin.y))
        pygame.draw.circle(surface, self.workspace_color, center, WORKSPACE_RADIUS)
        pygame.draw.circle(surface, pygame.Color("#0c7db1"), center, WORKSPACE_RADIUS, 4)

        for zone in self.tissue_zones:
            zone.draw(surface, self.origin)
        for aperture in self.apertures:
            aperture.draw(surface, self.origin)
        for bead in self.beads:
            bead.draw(surface, self.origin)
        for instrument in self.instruments:
            self._draw_instrument(surface, instrument)

        if self.flash_timer > 0:
            alpha = min(180, int(255 * (self.flash_timer / 0.3)))
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((220, 40, 40, alpha))
            surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def _draw_instrument(self, surface: pygame.Surface, instrument: Instrument) -> None:
        base = self.origin
        tip = base + instrument.tip
        pygame.draw.line(
            surface,
            instrument.color,
            (int(base.x), int(base.y)),
            (int(tip.x), int(tip.y)),
            4,
        )
        pygame.draw.circle(surface, instrument.color, (int(tip.x), int(tip.y)), 8)

    def _draw_title(self) -> None:
        assert self.screen and self.font_large and self.font_small
        lines = [
            self.font_large.render("LapDrop: Stealth Surgeon", True, pygame.Color("white")),
            self.font_small.render(
                f"Drill: {self.config.name} — press Enter to begin", True, pygame.Color("#8bd4ff")
            ),
        ]
        total_height = sum(line.get_height() for line in lines) + 16
        y = self.screen.get_height() // 2 - total_height // 2
        for surface_line in lines:
            rect = surface_line.get_rect(center=(self.screen.get_width() // 2, y))
            self.screen.blit(surface_line, rect)
            y += surface_line.get_height() + 8

    def _draw_running(self) -> None:
        assert self.screen and self.font_small
        timer_remaining = max(0.0, self.config.duration_seconds - self.elapsed_time)
        hud_lines = [
            f"Time: {timer_remaining:05.1f}s",
            f"Drops: {self.score.drops}/{self.config.target_drops}",
            f"Score: {self.score.score:04.0f}",
            f"Streak: {self.score.streak}",
        ]
        for index, text in enumerate(hud_lines):
            rendered = self.font_small.render(text, True, pygame.Color("#e6f7ff"))
            self.screen.blit(rendered, (24, 24 + index * 24))

    def _draw_results(self) -> None:
        assert self.screen and self.font_small and self.font_large and self.session_result
        result = self.session_result
        lines = [
            self.font_large.render("Results", True, pygame.Color("white")),
            self.font_small.render(
                f"Score: {result.breakdown.score:0.0f} — Grade {result.breakdown.grade()}",
                True,
                pygame.Color("#a6f5ff"),
            ),
            self.font_small.render(
                f"Drops: {result.breakdown.drops}  Misses: {result.breakdown.misses}  Tissue: {result.breakdown.tissue_contacts}",
                True,
                pygame.Color("#d0f0ff"),
            ),
            self.font_small.render(
                f"Perfect drops: {result.breakdown.perfect_drops}  Best streak: {result.breakdown.best_streak}",
                True,
                pygame.Color("#d0f0ff"),
            ),
            self.font_small.render(
                f"Telemetry saved to: {result.telemetry_path}",
                True,
                pygame.Color("#82cfff"),
            ),
            self.font_small.render(
                "Press Enter to return to title", True, pygame.Color("#82cfff")
            ),
        ]
        total_height = sum(line.get_height() for line in lines) + 16
        y = self.screen.get_height() // 2 - total_height // 2
        for surface_line in lines:
            rect = surface_line.get_rect(center=(self.screen.get_width() // 2, y))
            self.screen.blit(surface_line, rect)
            y += surface_line.get_height() + 6

    def _build_apertures(self, config: DrillConfig) -> list[Aperture]:
        apertures: list[Aperture] = []
        for ap in config.apertures:
            motion = None
            if ap.motion:
                motion = {"kind": ap.motion.kind, **ap.motion.params}
            aperture = Aperture(
                id=ap.id,
                center=Vec2(ap.position),
                radius=ap.radius,
                motion=motion,
            )
            aperture.update(0.0)
            apertures.append(aperture)
        return apertures

    def _build_tissue(self, config: DrillConfig) -> list[TissueZone]:
        return [
            TissueZone(id=tz.id, center=Vec2(tz.center), size=Vec2(tz.size), penalty=tz.penalty)
            for tz in config.tissue_zones
        ]


def run(drill_path: str | Path | None = None) -> None:
    LapDropGame(drill_path).run()


def main() -> None:  # pragma: no cover - manual invocation helper
    parser = argparse.ArgumentParser(description="Run LapDrop: Stealth Surgeon drills")
    parser.add_argument("drill", nargs="?", help="Path to a drill JSON file")
    args = parser.parse_args()
    run(args.drill)


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
