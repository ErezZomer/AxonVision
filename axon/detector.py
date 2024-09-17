import cv2
import imutils

from multiprocessing import Queue, Condition

from shared_frame import SharedFrame
class Detector:
    def __init__(self,
                 sf: SharedFrame,
                 out_queue: Queue,
                 new_frame: Condition,
                 new_detection: Condition,
                 debug: bool = False) -> None:
        self._sf = sf
        self._out_queue = out_queue
        self._frame_cond = new_frame
        self._detection_cond = new_detection
        
    
    def run(self):
        counter = 0
        prev_frame = None
        while True:
            with self._frame_cond:
                print(f"{self.__class__.__name__}: waiting for frame condition")
                self._frame_cond.wait()
                print(f"{self.__class__.__name__}: reading frame from buffer")
                frame = self._sf.read_frame()
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if counter == 0:
                prev_frame = gray_frame
                counter += 1

            diff = cv2.absdiff(gray_frame, prev_frame)
            thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            prev_frame = gray_frame
            counter += 1
            detections = {
                "detections": cnts
            }
            with self._detection_cond:
                print(f"{self.__class__.__name__}: sending detections")
                self._out_queue.put(detections)
                self._detection_cond.notify()
