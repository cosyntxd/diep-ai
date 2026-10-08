#    Name,       Hex Color,   Sides,  Radius,   Health,  Experience,  Body Damage
SHAPES = [
    ("Square",    "#FFE869",    4,     15.0,      10.0,      10.0,      8.0),
    ("Triangle",  "#FC7677",    3,     17.0,      30.0,      25.0,      8.0),
    ("Pentagon",  "#768DFC",    5,     25.0,     100.0,     130.0,     12.0),
    ("Hexagon",   "#FF8954",    6,     38.0,    1500.0,    1500.0,     16.0),
    ("CrasherS",  "#F177DD",    3,     10.0,      10.0,      15.0,     10.0),
    ("CrasherL",  "#F177DD",    3,     16.0,      30.0,      25.0,     18.0),
]

class Shape(GameObject):
    def __init__(self):
        pass
