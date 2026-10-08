import math

CELL_SIZE = 32

class EntityTracker:
    def __init__(self):
        self.next_uuid: int = 0
        self.grid: dict[tuple[int, int], set[GameObject]] = {}
        self.entities: dict[int, GameObject] = {}
        self.to_add: list[GameObject] = []
        self.to_delete: list[GameObject] = []

    # cannot modify len(self.entities) while iterating
    def add_immediate(self, e: "GameObject"):
        e.uuid = self.next_uuid
        self.next_uuid += 1
        e.tracker = self
        self.entities[e.uuid] = e
        self.grid.setdefault(e.get_chunk(), set()).add(e)

    def add_defered(self, e: "GameObject"):
        e.uuid = self.next_uuid
        self.next_uuid += 1
        # e.tracker = self # no ghost objects?
        self.to_add.append(e)

    def resolve_changes(self):
        for e in self.to_delete:
            assert e.mark_for_deletion


class GameObject:
    tracker: EntityTracker
    mark_for_deletion: float
    uuid: int

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


    # rect is defined as center, size
    def in_rect(self, c_x, c_y, w, h):
        good_x = (abs(self.pos_x - c_x) <= w + self.radius)
        good_y = (abs(self.pos_y - c_y) <= h + self.radius)
        return (good_x and good_y)

    def collides_width(self, other):
        distance = math.hypot((self.pos_x - other.pos_x), (self.pos_y - other.pos_y))
        return distance <= (self.radius + other.radius)

    def apply_impulse(self, fx: float, fy: float):
        self.v_x += fx / self.mass
        self.v_y += fy / self.mass

    def tick_position(self):
        self.pos_x += self.v_x
        self.pos_y += self.v_y

        self.v_x *= self.v_resistance
        self.v_y *= self.v_resistance

        self.angle += self.ang_v
        self.ang_v *= self.ang_v_resistance

    def get_chunk(self) -> tuple[int,int]:
        return math.floor(self.pos_x / CELL_SIZE), math.floor(self.pos_y / CELL_SIZE)

    def tick(self):
        self.tick_position()
        print("Override Me")
