import argparse
import multiprocessing as mp

from consts import DELAY
from streamer import Streamer
from detector import Detector
from viewer import Viewer

class Axon:
    def __init__(self, file_path: str, debug: bool = False) -> None:
        self._new_frame_cond = mp.Condition()
        self._new_detection_cond = mp.Condition()
        self._viewed_cond = mp.Condition()
        self._detections_q = mp.Queue()
        self._debug = debug
        self._streamer = Streamer(file_path, self._new_frame_cond, self._viewed_cond, DELAY, self._debug)
        buffer = self._streamer.buffer
        self._detector = Detector(buffer, self._detections_q, self._new_frame_cond, self._new_detection_cond, self._debug)
        self._viewer = Viewer(buffer, self._detections_q, self._new_detection_cond, self._viewed_cond, DELAY, self._debug)
        self._processes = []
        for obj in (self._streamer, self._detector, self._viewer):
            self._processes.append(mp.Process(target=obj.run))
    
    def run(self):
        with self._viewed_cond:
            self._viewed_cond.notify_all()
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