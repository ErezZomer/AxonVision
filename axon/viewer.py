from datetime import datetime
import multiprocessing as mp
import multiprocessing.shared_memory as sm

import cv2

from consts import DELAY
from shared_frame import SharedFrame

class Viewer:
    def __init__(self, 
                 sf: SharedFrame, 
                 in_queue: mp.Queue, 
                 detection: mp.Condition, 
                 viewed: mp.Condition, 
                 delay: int = DELAY,
                 debug: bool = False) -> None:
        self._sf = sf
        self._in_queue = in_queue
        self._detection_cond = detection
        self._viewed_cond = viewed
        self._delay = delay
        self._debug = debug
    def add_time(self, image):
        # Get the current time
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        # Define the font, scale, color, and thickness
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (255, 255, 255)  # White color in BGR
        thickness = 2

        # Get the text size to position the text at the bottom
        (text_width, text_height), _ = cv2.getTextSize(current_time, font, font_scale, thickness)
        text_x = 10  # X-coordinate for the text
        text_y = image.shape[0] - 690  # Y-coordinate for the text (near the bottom)

        # Put the text on the image
        cv2.putText(image, current_time, (text_x, text_y), font, font_scale, color, thickness)

        return image

    def add_detections(self, image):
        print(f"{self.__class__.__name__}: waiting for detections")
        msg = self._in_queue.get()
        print(f"{self.__class__.__name__}: got new detections")
        detections = msg.get("detections", [])
        
        for (x1, y1, x2, y2) in detections:
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Red rectangle with thickness 2
        
        return image

    def add_blur(self, image):
        #TODO
        return image

    def run(self):
        with self._viewed_cond:
            self._viewed_cond.notify()
        while True:
            #with self._detection_cond:
            #    print(f"{self.__class__.__name__}: waiting for detection condition")
            #    self._detection_cond.wait()
            image = self._sf.read_frame()
            image = self.add_time(image)
            #image = self.add_detections(image)
            #image= self.add_blur(image)            

                # Display the frame using OpenCV
            cv2.imshow("Detections and Time", image)
            with self._viewed_cond:
                self._viewed_cond.notify()
    
                # Wait for a keypress to close the window
            cv2.waitKey(self._delay)
        
        def __del__(self):
            cv2.destroyAllWindows()