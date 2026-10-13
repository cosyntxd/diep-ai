import math

CELL_SIZE = 32


class HashGrid:
    def __init__(self, cell_size: int = CELL_SIZE):
        self.cell_size = cell_size
        self.cells: dict[tuple[int, int], set] = {}
        self.chunk_of: dict = {}

    def cell_of(self, x: float, y: float) -> tuple[int, int]:
        return math.floor(x / self.cell_size), math.floor(y / self.cell_size)

    def insert(self, e) -> None:
        chunk = self.cell_of(e.pos_x, e.pos_y)
        self.cells.setdefault(chunk, set()).add(e)
        self.chunk_of[e] = chunk

    def remove(self, e) -> None:
        chunk = self.chunk_of.pop(e, None)
        if chunk is None:
            return
        bucket = self.cells.get(chunk)
        if bucket is not None:
            bucket.discard(e)
            if not bucket:
                del self.cells[chunk]

    def update(self, e) -> None:
        chunk = self.cell_of(e.pos_x, e.pos_y)
        if self.chunk_of.get(e) == chunk:
            return
        self.remove(e)
        self.insert(e)

    # account for radius????
    def query_rect(self, c_x: float, c_y: float, w: float, h: float, radius: float = 0.0) -> list:
        results = []
        min_x = math.floor((c_x - w - radius) / self.cell_size)
        max_x = math.floor((c_x + w + radius) / self.cell_size)
        min_y = math.floor((c_y - h - radius) / self.cell_size)
        max_y = math.floor((c_y + h + radius) / self.cell_size)
        for gx in range(min_x, max_x + 1):
            for gy in range(min_y, max_y + 1):
                results.extend(self.cells.get((gx, gy), ()))
        return results

    def query_circle(self, x: float, y: float, r: float) -> list:
        return self.query_rect(x, y, 0.0, 0.0, r)
