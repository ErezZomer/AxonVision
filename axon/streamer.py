import argparse
from multiprocessing import Condition, Queue
import numpy as np
import cv2
import uuid 

from consts import MAX_QUEUE_SIZE

class Streamer:
    def __init__(self, file_path: str, frame_q: Queue, delay: int = 25, debug: bool = False):
        self._path = file_path
        self._cap = None
        #ret, self._frame_array = self._cap.read()
        #if not ret:
        #    raise Exception(f"Failed to read file: {self._path}")
        #self._shm = SharedMemory(name=self._file_name, create=True, size=self._frame_array.nbytes)
        #self._sf = np.ndarray(shape=self._frame_array.shape, dtype=self._frame_array.dtype, buffer=self._shm.buf)
        #self._sf = SharedFrame(self._file_name, self._frame_array.shape, self._frame_array.nbytes, self._frame_array.dtype)
        self._frame_q = frame_q
        self.delay = delay
        self._debug = debug

    def _init_capture(self):
        if not self._cap:
            self._cap = cv2.VideoCapture(self._path)

        # Check if video opened successfully
        if not self._cap.isOpened():
            print("Error: Could not open video file.")
            exit()

    def __del__(self):
        # Release the video capture object
        if self._cap:
            self._cap.release()

        # Close all OpenCV windows
        cv2.destroyAllWindows()
    
    def run(self):
        # Read and display video frames in a loop
        self._init_capture()
        while self._cap.isOpened():
            print(f"{self.__class__.__name__}: reading frame from file")
            ret, frame = self._cap.read()
                

            # Break the loop when no more frames are available
            if not ret:
                print("Reached the end of the video.")
                break

            msg = {
                "frame": frame,
                "frame_id": str(uuid.uuid4())}
            # send the current frame to detector.
            print(f"{self.__class__.__name__}: writing frame to queue")

            self._frame_q.put(msg)

            # display the current frame,
            if self._debug:
                cv2.imshow('Video Stream', frame)

            # Wait for 25ms before moving on to the next frame
            # If 'q' key is pressed, break the loop and close the video
            if cv2.waitKey(self.delay) & 0xFF == ord('q'):
                break

        self.__del__()


if __name__ == "__main__":
    path = "/home/erez/repos/interviewing/AxonVision/data/videos/People - 6387.mp4"
    q = Queue(MAX_QUEUE_SIZE)
    s = Streamer(path, q)
    s.run()