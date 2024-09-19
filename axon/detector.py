import cv2
import imutils

from multiprocessing import Queue, Condition

class Detector:
    def __init__(self,
                 frames_q: Queue,
                 detections_q: Queue,
                 debug: bool = False) -> None:
        self._frames_q = frames_q
        self._detections_q = detections_q
        self._debug = debug
    
    def run(self):
        counter = 0
        prev_frame = None
        while True:
            print(f"{self.__class__.__name__}: waiting for frame msg")
            msg = self._frames_q.get()
            frame = msg["frame"]
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
            msg["counturs"] = cnts
            print(f"{self.__class__.__name__}: sending detections")
            self._detections_q.put(msg)
