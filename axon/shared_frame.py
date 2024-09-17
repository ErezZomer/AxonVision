from typing import Tuple
from multiprocessing.shared_memory import SharedMemory
import numpy as np


class SharedFrame:
    def __init__(self, name: str, shape: Tuple[int, int], size: int, dtype: np.uint8) -> None:
        self._shm = SharedMemory(name=name, create=True, size=size)
        self._sf = np.ndarray(shape=shape, dtype=dtype, buffer=self._shm.buf)
    
    def read_frame(self):
        return self._sf[:]
    
    def write_frame(self, frame):
        self._sf[:]  = frame[:]
    
    def name(self):
        return self._shm.name
    
    def __del__(self):
        self._shm.close()
        self._shm.unlink()