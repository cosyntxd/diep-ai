import math
import random
from enum import IntEnum

from simulator.entities.entity import EntityTracker
from simulator.entities.shapes import Shape
from simulator.entities.tanks import TanksEnum, TankAgent
from simulator.entities.projectile import Bullet

ARENA_WIDTH = 5000.0
ARENA_HEIGHT = 5000.0
MAX_OUTER_SHAPES = 500
MAX_NEST_SHAPES = 80
MAX_ALPHA_PENTAGONS = 4
NEST_RADIUS = 600.0
SHAPE_SPAWN_INTERVAL = 1
ELASTICITY = 1.5


class GameMode(IntEnum):
    FFA = 0
    TEAMS_4 = 1


# spawns players and force spawns tiles and such
class Engine:
    def __init__(self, width: float = ARENA_WIDTH, height: float = ARENA_HEIGHT,
                 gamemode: GameMode = GameMode.FFA):
        self.width = width
        self.height = height
        self.gamemode = gamemode

        self.tracker = EntityTracker()
        self.ticks = 0

    def step(self) -> None:
        self.ticks += 1
        self.tracker.tick_all()
        self.resolve_shape_collisions()
        self.enforce_borders()
        self.tracker.resolve_changes()

        if self.ticks % SHAPE_SPAWN_INTERVAL == 0:
            self.try_spawn_shapes()

    def _in_nest(self, x: float, y: float) -> bool:
        return math.hypot(x - self.width / 2, y - self.height / 2) <= NEST_RADIUS

    def find_spawn_position(self, clearance: float = 60.0, in_nest: bool = False) -> tuple[float, float]:
        margin = 50.0
        cx, cy = self.width / 2, self.height / 2
        x, y = cx, cy
        for _ in range(10):
            if in_nest:
                angle = random.uniform(0, math.tau)
                dist = NEST_RADIUS * math.sqrt(random.random())
                x = cx + math.cos(angle) * dist
                y = cy + math.sin(angle) * dist
            else:
                x = random.uniform(margin, self.width - margin)
                y = random.uniform(margin, self.height - margin)
                if self._in_nest(x, y):
                    continue
            if not self.tracker.query_rect(x, y, clearance, clearance):
                return x, y
        return x, y

    def spawn_player(self, id: int, tank_type: TanksEnum = TanksEnum.TANK,
                     team: int = 0) -> TankAgent:
        pos_x, pos_y = self.find_spawn_position(clearance=120.0, in_nest=False)
        tank = TankAgent(id=id, tank_type=tank_type, pos_x=pos_x, pos_y=pos_y, team=team)
        return self.tracker.add_immediate(tank)

    def try_spawn_shapes(self) -> None:
        outer_count = 0
        nest_count = 0
        alpha_count = 0
        for e in self.tracker.entities.values():
            if isinstance(e, Shape):
                if e.shape_type == "AlphaPentagon":
                    alpha_count += 1
                if self._in_nest(e.pos_x, e.pos_y):
                    nest_count += 1
                else:
                    outer_count += 1

        if outer_count + nest_count >= MAX_OUTER_SHAPES + MAX_NEST_SHAPES:
            return
        if outer_count < MAX_OUTER_SHAPES:
            self.force_spawn_shape(in_nest=False)
        if nest_count < MAX_NEST_SHAPES:
            self.force_spawn_shape(in_nest=True, allow_alpha=alpha_count < MAX_ALPHA_PENTAGONS)

    def force_spawn_shape(self, shape_type: str | None = None, in_nest: bool = False,
                          allow_alpha: bool = True) -> Shape:
        pos_x, pos_y = self.find_spawn_position(clearance=60.0, in_nest=in_nest)

        if shape_type is None:
            if in_nest:
                r = random.random()
                if allow_alpha and r < 0.05:
                    shape_type = "AlphaPentagon"
                elif r < 0.25:
                    shape_type = "CrasherS"
                elif r < 0.30:
                    shape_type = "CrasherL"
                else:
                    shape_type = "Pentagon"
            else:
                r = random.random()
                if r < 0.03:
                    shape_type = "Pentagon"
                elif r < 0.20:
                    shape_type = "Triangle"
                else:
                    shape_type = "Square"

        shape = Shape(shape_type=shape_type, pos_x=pos_x, pos_y=pos_y)
        return self.tracker.add_immediate(shape)

    def resolve_shape_collisions(self) -> None:
        for e in self.tracker.entities.values():
            if not isinstance(e, Shape):
                continue
            for other in e.query_collisions():
                if not isinstance(other, Shape) or e.uuid >= other.uuid:
                    continue

                angle = e.angle_to(other)
                total_r = e.radius + other.radius
                cos_a, sin_a = math.cos(angle), math.sin(angle)

                e.apply_impulse(-ELASTICITY * (other.radius / total_r) * cos_a,
                                -ELASTICITY * (other.radius / total_r) * sin_a)
                other.apply_impulse(ELASTICITY * (e.radius / total_r) * cos_a,
                                    ELASTICITY * (e.radius / total_r) * sin_a)

    def enforce_borders(self) -> None:
        for e in self.tracker.entities.values():
            clamped = False
            if e.pos_x < e.radius:
                e.pos_x = e.radius
                e.v_x = abs(e.v_x)
                clamped = True
            elif e.pos_x > self.width - e.radius:
                e.pos_x = self.width - e.radius
                e.v_x = -abs(e.v_x)
                clamped = True

            if e.pos_y < e.radius:
                e.pos_y = e.radius
                e.v_y = abs(e.v_y)
                clamped = True
            elif e.pos_y > self.height - e.radius:
                e.pos_y = self.height - e.radius
                e.v_y = -abs(e.v_y)
                clamped = True

            if clamped:
                self.tracker.grid.update(e)
