import math
from enum import IntEnum

from .entity import GameObject
from .projectile import Bullet

# todo: fog of war


class TanksEnum(IntEnum):
    TANK = 0
    TWIN = 1
    FLANK = 2
    SNIPER = 3
    MACHINE_GUN = 4
    UNUSED1 = 5


# (angle_offset, reload, bullet_speed, bullet_damage, bullet_lifetime, bullet_radius, spread, count)
BARREL_LAYOUTS = {

    TanksEnum.TANK: [0]*8
}


class TankAgent(GameObject):
    def __init__(self, id: int, tank_type: TanksEnum = TanksEnum.TANK,
                 pos_x: float = 0.0, pos_y: float = 0.0, radius: float = 20.0,
                 health: float = 100.0, team: int = 0, color: str = "#00B2E1"):
        super().__init__(pos_x=pos_x, pos_y=pos_y, radius=radius, mass=radius)
        self.id = id
        self.tank_type = TanksEnum(tank_type)
        self.team = team
        self.color = color
        self.max_health = health
        self.health = health

        self.experience = 0
        self.regen = 0.0

        # management
        self.last_fired_tick: int = -1
        self.mouse_relative: tuple[float, float] = (0.0, 0.0)
        self.last_fired = 0 # idk how to do multi barrels

        # upgradables
        self.upgrade_regen = 0
        self.upgrade_health = 0
        self.upgrade_bodydmg = 0
        self.upgrade_bspeed = 0
        self.upgrade_penetration = 0
        self.upgrade_damage = 0
        self.upgrade_reload = 0
        self.upgrade_mvspeed = 0

    def aim_relative(self):
        dx, dy = self.mouse_relative
        if dx == 0.0 and dy == 0.0:
            return
        self.angle = math.atan2(dy, dx)

    def tick(self):
        if self.regen:
            self.health = min(self.max_health, self.health + self.regen)
        self.tick_position()
