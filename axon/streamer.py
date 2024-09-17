import argparse
from multiprocessing import Condition, Queue
from multiprocessing.shared_memory import SharedMemory
from shared_frame import SharedFrame
import numpy as np
import cv2

data = {
    "frame": None,
    "detections": None,
    "detected": False,
    "Viewed": False
    
}


class Streamer:
    def __init__(self, file_path, frame: Condition = None, viewed: Condition = None, delay: int = 25, debug: bool = False):
        self._path = file_path
        self._file_name = file_path.rsplit("/")[-1]
        self.cap = cv2.VideoCapture(self._path)

        # Check if video opened successfully
        if not self.cap.isOpened():
            print("Error: Could not open video file.")
            exit()
        ret, self._frame_array = self.cap.read()
        if not ret:
            raise Exception(f"Failed to read file: {self._path}")
        #self._shm = SharedMemory(name=self._file_name, create=True, size=self._frame_array.nbytes)
        #self._sf = np.ndarray(shape=self._frame_array.shape, dtype=self._frame_array.dtype, buffer=self._shm.buf)
        self._sf = SharedFrame(self._file_name, self._frame_array.shape, self._frame_array.nbytes, self._frame_array.dtype)
        self._frame_cond = frame
        self._viewed_cond = viewed
        self.delay = delay
        self._debug = debug

    @property
    def buffer(self):
        if self._sf:
            return self._sf
        else:
            raise Exception("Failed to initlized shared memory!")

    def __del__(self):
        # Release the video capture object
        self.cap.release()

        # Close all OpenCV windows
        cv2.destroyAllWindows()
    
    def run(self):
        # Read and display video frames in a loop
        while self.cap.isOpened():
            with self._viewed_cond:
                print(f"{self.__class__.__name__}: waiting for viewed condition")
                self._viewed_cond.wait()
            print(f"{self.__class__.__name__}: reading frame from file")
            ret, frame = self.cap.read()
                

            # Break the loop when no more frames are available
            if not ret:
                print("Reached the end of the video.")
                break

            # send the current frame to detector.
            print(f"{self.__class__.__name__}: writing frame to buffer")
            self._sf.write_frame(frame)
            with self._frame_cond:
                self._frame_cond.notify()

            # display the current frame,
            if self._debug:
                cv2.imshow('Video Stream', frame)

            # Wait for 25ms before moving on to the next frame
            # If 'q' key is pressed, break the loop and close the video
            if cv2.waitKey(self.delay) & 0xFF == ord('q'):
                break

        self.__del__()


