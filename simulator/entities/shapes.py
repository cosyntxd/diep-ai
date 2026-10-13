from .entity import GameObject

#    Name,       Hex Color,   Sides,  Radius,   Health,  Experience,  Body Damage
SHAPES = [
    ("Square",    "#FFE869",    4,     15.0,      10.0,      10.0,      8.0),
    ("Triangle",  "#FC7677",    3,     17.0,      30.0,      25.0,      8.0),
    ("Pentagon",  "#768DFC",    5,     25.0,     100.0,     130.0,     12.0),
    ("Hexagon",   "#FF8954",    6,     38.0,    1500.0,    1500.0,     16.0),
    ("CrasherS",  "#F177DD",    3,     10.0,      10.0,      15.0,     10.0),
    ("CrasherL",  "#F177DD",    3,     16.0,      30.0,      25.0,     18.0),
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

    def tick(self):
        self.tick_position()
