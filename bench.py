import math
import time
import random
start_time = time.perf_counter()
 
class ObjectPos():
    def __init__(self, x, y):
        self.x = x
        self.y = y

objs = []
for i in range(500):
    x = random.uniform(-10, 10)
    y = random.uniform(-10, 10)
    objs.append(ObjectPos(x, y))

hits = 0
for o in objs:
    for o2 in objs:
        if math.hypot(o.x - o2.x, o2.y - o2.y) < 0.01:
            hits += 1

end_time = time.perf_counter()

elapsed_ms = (end_time - start_time) * 1000
print(elapsed_ms, hits)