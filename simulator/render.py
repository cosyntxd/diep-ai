import os
import shutil
import av
import cv2
import numpy as np
from queue import Queue
from threading import Thread
from simulator.engine import Engine


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
        image = np.zeros((2000, 2000, 3), dtype=np.uint8)
        for pos in range(0, 2000, 100):
            cv2.line(image, (pos, 0), (pos, 1999), (255, 255, 255), 4)
            cv2.line(image, (0, pos), (1999, pos), (255, 255, 255), 4)

        self.buffered_frames.put(image, timeout=30)
