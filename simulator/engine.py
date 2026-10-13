from simulator.entities import *


# spawns players and force spawns tiles and such
# tiles divide by themselves
class Engine:
    def __init__(self, render = False):
        self.tracker = EntityTracker()
        self.render = render

    def step(self):
        self.tracker.tick_all()
        self.tracker.resolve_changes()
