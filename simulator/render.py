import math
import os
import shutil
import av
import cv2
import numpy as np
from queue import Queue
from threading import Thread
from simulator.engine import Engine
from simulator.entities.shapes import Shape
from simulator.entities.tanks import TankAgent
from simulator.entities.projectile import Bullet


def hex_to_bgr(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)


def darken(bgr: tuple[int, int, int], factor: float = 0.7) -> tuple[int, int, int]:
    return (int(bgr[0] * factor), int(bgr[1] * factor), int(bgr[2] * factor))


class Renderer:
    def __init__(self, fps: int = 30):
        self.buffered_frames = Queue(maxsize=256)
        self.output_path = "render.m3u8"
        self.output_chunks = os.path.join(os.path.dirname(self.output_path) or ".", "chunks")
        shutil.rmtree("chunks", ignore_errors=True)

        self.fps = fps
        self.writer = None
        self.stream = None

        self.writer_thread = Thread(target=self._writer_thread_func, daemon=False)
        self.writer_thread.start()

    def shutdown(self):
        self.buffered_frames.put(None)
        self.writer_thread.join()

    def _writer_thread_func(self):
        try:
            while True:
                new_frame = self.buffered_frames.get()
                if new_frame is None:
                    self.buffered_frames.task_done()
                    break

                if self.writer is None:
                    height, width = new_frame.shape[:2]

                    os.makedirs(self.output_chunks, exist_ok=True)

                    self.writer = av.open(
                        self.output_path,
                        mode="w",
                        format="hls",
                        options={
                            "hls_time": "8",
                            "hls_list_size": "0",
                            "hls_playlist_type": "event",
                            "hls_base_url": "chunks/",
                            "hls_segment_filename": os.path.join(self.output_chunks, "seg_%05d.ts"),
                        },
                    )

                    self.stream = self.writer.add_stream(
                        "libx264",
                        rate=self.fps,
                        options={
                            "preset": "ultrafast",
                            "crf": "23",
                            "g": str(self.fps * 8),
                            "sc_threshold": "0",
                        },
                    )
                    self.stream.width = width
                    self.stream.height = height
                    self.stream.pix_fmt = "yuv420p"

                frame = av.VideoFrame.from_ndarray(new_frame, format="bgr24")
                self.writer.mux(self.stream.encode(frame))
                self.buffered_frames.task_done()

        finally:
            if self.writer is not None:
                self.writer.mux(self.stream.encode(None))
                self.writer.close()

    def render(self, engine: Engine) -> None:
        w, h = 2000, 2000
        sx = w / engine.width
        sy = h / engine.height
        scale = min(sx, sy)

        image = np.full((h, w, 3), 205, dtype=np.uint8)

        for x in range(0, w, 100):
            cv2.line(image, (x, 0), (x, h - 1), (190, 190, 190), 2)
        for y in range(0, h, 100):
            cv2.line(image, (0, y), (w - 1, y), (190, 190, 190), 2)

        for e in engine.tracker.entities.values():
            color = hex_to_bgr(e.color)
            outline = darken(color)
            cx, cy = int(e.pos_x * sx), int(e.pos_y * sy)
            r = max(1, int(e.radius * scale))

            if isinstance(e, Shape):
                pts = np.array([
                    [
                        int((e.pos_x + math.cos(e.angle + i * math.tau / e.sides) * e.radius) * sx),
                        int((e.pos_y + math.sin(e.angle + i * math.tau / e.sides) * e.radius) * sy),
                    ]
                    for i in range(e.sides)
                ], dtype=np.int32)
                cv2.fillPoly(image, [pts], color, cv2.LINE_AA)
                cv2.polylines(image, [pts], True, outline, 1, cv2.LINE_AA)

            elif isinstance(e, TankAgent):
                bx = int((e.pos_x + math.cos(e.angle) * e.radius * 1.6) * sx)
                by = int((e.pos_y + math.sin(e.angle) * e.radius * 1.6) * sy)
                cv2.line(image, (cx, cy), (bx, by), (110, 110, 110), max(1, int(r * 0.8)), cv2.LINE_AA)
                cv2.circle(image, (cx, cy), r, color, -1, cv2.LINE_AA)
                cv2.circle(image, (cx, cy), r, outline, 1, cv2.LINE_AA)

            elif isinstance(e, Bullet):
                cv2.circle(image, (cx, cy), r, color, -1, cv2.LINE_AA)
                cv2.circle(image, (cx, cy), r, outline, 1, cv2.LINE_AA)

        self.buffered_frames.put(image, timeout=30)
