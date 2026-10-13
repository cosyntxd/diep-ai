import math
from .entity import GameObject


class Bullet(GameObject):
    def __init__(self, owner, angle: float, speed: float, damage: float,
                 lifetime: int, radius: float = 6.0):
        super().__init__(
            pos_x=owner.pos_x + math.cos(angle) * owner.radius,
            pos_y=owner.pos_y + math.sin(angle) * owner.radius,
            radius=radius,
            mass=radius,
        )
        self.owner = owner
        self.owner_id = owner.uuid
        self.team = owner.team
        self.color = owner.color
        self.damage = damage
        self.lifetime = lifetime
        self.age = 0
        self.angle = angle
        self.v_x = math.cos(angle) * speed
        self.v_y = math.sin(angle) * speed
        self.v_resistance = 1.0

    def tick(self):
        self.tick_position()
        self.age += 1
        if self.age >= self.lifetime:
            self.remove()
