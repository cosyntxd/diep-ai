import math
import random
from .entity import GameObject

#    Name,           Hex Color,   Sides,  Radius,   Health,  Experience,  Body Damage
SHAPES = [
    ("Square",        "#FFE869",    4,     15.0,      10.0,      10.0,      8.0),
    ("Triangle",      "#FC7677",    3,     17.0,      30.0,      25.0,      8.0),
    ("Pentagon",      "#768DFC",    5,     25.0,     100.0,     130.0,     12.0),
    ("AlphaPentagon", "#768DFC",    5,     55.0,    3000.0,    3000.0,     20.0),
    ("CrasherS",      "#F177DD",    3,     10.0,      10.0,      15.0,     10.0),
    ("CrasherL",      "#F177DD",    3,     16.0,      30.0,      25.0,     18.0),
]

SHAPE_DATA = {row[0]: row for row in SHAPES}


class Shape(GameObject):
    def __init__(self, shape_type: str = "Square", pos_x: float = 0.0, pos_y: float = 0.0):
        name, color, sides, radius, health, xp, body_damage = SHAPE_DATA[shape_type]
        super().__init__(pos_x=pos_x, pos_y=pos_y, radius=radius, mass=radius)
        self.shape_type = name
        self.color = color
        self.sides = sides
        self.max_health = health
        self.health = health
        self.experience = xp
        self.body_damage = body_damage

        self.angle = random.uniform(0, math.tau)
        self.ang_v = random.choice((-1, 1)) * random.uniform(0.005, 0.018)
        self.ang_v_resistance = 1.0

        self.drift_angle = random.uniform(0, math.tau)
        self.drift_turn = random.choice((-1, 1)) * random.uniform(0.002, 0.008)
        self.drift_force = random.uniform(0.02, 0.05)

        self.ticks = 0
        self.last_damage_tick = 0

    def tick(self):
        self.ticks += 1
        self.drift_angle += self.drift_turn
        self.v_x += math.cos(self.drift_angle) * self.drift_force
        self.v_y += math.sin(self.drift_angle) * self.drift_force

        if self.health < self.max_health and (self.ticks - self.last_damage_tick) >= 900:
            self.health = min(self.max_health, self.health + self.max_health / 250.0)

        self.tick_position()
