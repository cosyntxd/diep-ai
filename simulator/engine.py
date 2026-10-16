from simulator.entities.entity import EntityTracker
from simulator.entities.shapes import Shape
from simulator.entities.tanks import TanksEnum, TankAgent
from simulator.entities.projectile import Bullet


# spawns players and force spawns tiles and such
# tiles divide by themselves
class Engine:
    def __init__(self):
        self.tracker = EntityTracker()
        self.ticks = 0

    def step(self):
        self.ticks += 1
        self.tracker.tick_all()
        self.tracker.resolve_changes()
