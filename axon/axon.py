import argparse
import multiprocessing as mp

from consts import DELAY, MAX_QUEUE_SIZE
from streamer import Streamer
from detector import Detector
from viewer import Viewer

class Axon:
    def __init__(self, file_path: str, debug: bool = False) -> None:
        self._frames_q = mp.Queue(MAX_QUEUE_SIZE)
        self._detections_q = mp.Queue(MAX_QUEUE_SIZE)
        self._debug = debug
        self._streamer = Streamer(file_path, self._frames_q, DELAY, self._debug)
        self._detector = Detector(self._frames_q, self._detections_q, self._debug)
        self._viewer = Viewer(self._detections_q, DELAY, self._debug)
        self._processes = []
        objects = []
        objects.append(self._streamer)
        objects.append(self._detector)
        objects.append(self._viewer)
        for obj in objects:
            self._processes.append(mp.Process(target=obj.run))
    
    def run(self):
        for p in self._processes:
            p.start()
        
        for p in self._processes:
            p.join()
        
def main():
    parser = argparse.ArgumentParser(
        prog="Streamer",
        description="Sreams videos file from path.")
    parser.add_argument(
        "-p",
        "--path",
        #dest="username",
        #metavar="<USERNAME>",
        type=str,
        help="path to file",
        required=True
        )
    parser.add_argument(
        "-d",
        "--debug",
        #dest="username",
        #metavar="<USERNAME>",
        type=bool,
        help="debug flag",
        default=False,
        )
    
    args = parser.parse_args()
    print(args)
    axon = Axon(file_path=args.path, debug=args.debug)
    axon.run()
    
if __name__ == "__main__":
    main()