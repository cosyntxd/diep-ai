from time import sleep
import argparse
from simulator.engine import Engine
from simulator.render import Renderer

def main(args):
    engine = Engine()
    renderer = Renderer(fps=30)
    try:
        while True:
            engine.step()
            if args.render > 0 and engine.ticks % args.render == 0:
                renderer.render(engine)
            print(engine.ticks)
    except KeyboardInterrupt:
        renderer.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulator for game")
    parser.add_argument("-r", "--render", type=int, default=1, help="Saves game by a rendering every nth to render.mkv")
    args = parser.parse_args()
    main(args)
