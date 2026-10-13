import math
from .spatial import HashGrid, CELL_SIZE


class EntityTracker:
    def __init__(self):
        self.next_uuid: int = 0
        self.grid = HashGrid()
        self.entities: dict[int, GameObject] = {}
        self.to_add: list[GameObject] = []
        self.to_delete: list[GameObject] = []

    def tick_all(self):
        for e in list(self.entities.values()):
            e.tick

    # cannot modify len(self.entities) while iterating :(
    def add_immediate(self, e: GameObject) -> GameObject:
        e.uuid = self.next_uuid
        self.next_uuid += 1
        e.tracker = self
        self.entities[e.uuid] = e
        self.grid.insert(e)
        return e

    # if an object wants to clone or something idk
    def add_defered(self, e: GameObject) -> GameObject:
        e.uuid = self.next_uuid
        self.next_uuid += 1
        e.tracker = self
        self.to_add.append(e)
        return e

    def remove(self, e: GameObject) -> None:
        if e.mark_for_deletion:
            return
        e.mark_for_deletion = True
        self.to_delete.append(e)

    def resolve_changes(self) -> None:
        for e in self.to_add:
            self.entities[e.uuid] = e
            self.grid.insert(e)
        self.to_add.clear()

        for e in self.to_delete:
            assert e.mark_for_deletion
            self.grid.remove(e)
            self.entities.pop(e.uuid, None)
        self.to_delete.clear()

    def query_rect(self, c_x: float, c_y: float, w: float, h: float, radius: float = 0.0) -> list[GameObject]:
        return self.grid.query_rect(c_x, c_y, w, h, radius)

    # idk?
    def query_circle(self, x: float, y: float, r: float) -> list[GameObject]:
        return self.grid.query_circle(x, y, r)


class GameObject:
    tracker: EntityTracker
    uuid: int
    mark_for_deletion: bool

    pos_x: float
    pos_y: float

    v_x: float
    v_y: float

    v_resistance: float

    angle: float
    ang_v: float

    ang_v_resistance: float

    radius: float
    mass: float

    def __init__(self, pos_x: float = 0.0, pos_y: float = 0.0,
                 radius: float = 10.0, mass: float = 1.0):
        self.uuid = -1
        self.mark_for_deletion = False

        self.pos_x = pos_x
        self.pos_y = pos_y

        self.v_x = 0.0
        self.v_y = 0.0
        self.v_resistance = 0.9

        self.angle = 0.0
        self.ang_v = 0.0
        self.ang_v_resistance = 0.9

        self.radius = radius
        self.mass = mass

    # rect is defined as center, size
    def in_rect(self, c_x, c_y, w, h):
        good_x = (abs(self.pos_x - c_x) <= w + self.radius)
        good_y = (abs(self.pos_y - c_y) <= h + self.radius)
        return (good_x and good_y)

    def distance_to(self, other):
        return math.hypot((self.pos_x - other.pos_x), (self.pos_y - other.pos_y))

    def collides_with(self, other):
        return self.distance_to(other) <= (self.radius + other.radius)

    def distance_to_point(self, x, y):
        return math.hypot((self.pos_x - x), (self.pos_y - y))

    def angle_to(self, other):
        return math.atan2(other.pos_y - self.pos_y, other.pos_x - self.pos_x)

    def angle_to_point(self, x, y):
        return math.atan2(y - self.pos_y, x - self.pos_x)

    def apply_impulse(self, fx: float, fy: float):
        self.v_x += fx
        self.v_y += fy

    def tick_position(self):
        self.pos_x += self.v_x
        self.pos_y += self.v_y

        self.v_x *= self.v_resistance
        self.v_y *= self.v_resistance

        self.angle += self.ang_v
        self.ang_v *= self.ang_v_resistance

        self.tracker.grid.update(self)

    def get_chunk(self) -> tuple[int, int]:
        return math.floor(self.pos_x / CELL_SIZE), math.floor(self.pos_y / CELL_SIZE)

    def remove(self):
        self.tracker.remove(self)

    def tick(self):
        self.tick_position()
        print("Override Me")
