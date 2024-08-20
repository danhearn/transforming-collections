from abc import ABC, abstractmethod
from PIL import Image, ImageSequence
import cv2

class Media(ABC):
    def __init__(self, path):
        self.path = path
        self.ID = path.split('/')[-1].split('.')[0]

        self._frame = 0
        self._frame_data = None
        self._frame_duration = None

        self.size = None
        self.frame_count = None
        self.texture_UUID = None
        pass
    
    @abstractmethod
    def go_to_next_frame(self):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def restart(self):
        pass

    @abstractmethod
    def get_frame_duration(self):
        pass

    @abstractmethod
    def get_size(self):
        pass

    @abstractmethod
    def get_frame_count(self):
        pass

    @abstractmethod
    def is_finished():
        pass

class Gif(Media):
    def __init__(self, path):
        super().__init__(path)
        self.capture = None
        self.open()
        self.size = self.get_size()
        self.frame_count = self.get_frame_count()        
        self.close()

    def go_to_next_frame(self):
        self._frame += 1
        self._frame %= len(self.frame_count)
        active_frame = ImageSequence.Iterator(self.capture)[self._frame]
        frame_rgb = active_frame.convert("RGB")
        image_bytes = frame_rgb.tobytes("raw", "RGBX", 0, -1)
        self._frame_data = image_bytes

    def open(self):
        if self.capture is None:
            self.capture = Image.open(self.path)
        self.restart()
        active_frame = ImageSequence.Iterator(self.capture)[self._frame]
        frame_rgb = active_frame.convert("RGB")
        image_bytes = frame_rgb.tobytes("raw", "RGBX", 0, -1)
        self._frame_data = image_bytes
    
    def close(self):
        if self.capture is not None:
            self.capture.close()
            self.capture = None
    
    def restart(self):
        self._frame = 0
    
    def get_frame_duration(self):
        active_frame = ImageSequence.Iterator(self.capture)[self._frame]
        return active_frame.info['duration']/1000
    
    def get_size(self):
        if self.size is None:
            self.size = self.capture.size
        return self.size
    
    def get_frame_count(self):
        if self.frame_count is None:
            self.frame_count = [frame.copy() for frame in ImageSequence.Iterator(self.capture)]
        return self.frame_count
    
    def is_finished(self):
        return self._frame >= len(self.frame_count) - 1


class Video(Media):
    def __init__(self, path):
        super().__init__(path)
        self.capture = None
        self.open()
        self.size = self.get_size()
        self._frame_duration = self.get_frame_duration()
        self.frame_count = self.get_frame_count()
        self.pbo_UUID = None
        self.close()
        self._next_frame_data = None
        self._buffer_index = 0
    
    def go_to_next_frame(self):
        if self.capture is not None and self.capture.isOpened():
            # Move the next frame data to the current frame data
            # self._frame_data = self._next_frame_data

            # Read the next frame
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                self._frame_data = frame.data.tobytes()
    
    def open(self):
        if self.capture is None or not self.capture.isOpened():
            self.capture = cv2.VideoCapture(self.path)
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        self.restart()

    def close(self):
        if self.capture is not None and self.capture.isOpened():
            self.capture.release()
            self.capture = None
    
    def restart(self):
        self._frame = 0
        if self.capture is not None and self.capture.isOpened():
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, self._frame)

    def get_size(self):
        if self.size is None:
            self.size = (int(self.capture.get(3)), int(self.capture.get(4)))
        return self.size

    def get_frame_duration(self):
        if self._frame_duration is None:
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            self._frame_duration = 1 / fps
        return self._frame_duration
    
    def get_frame_count(self):
        if self.frame_count is None:
            self.frame_count = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        return self.frame_count
    
    def is_finished(self):
        if self.capture is not None and self.capture.isOpened():
            current_frame = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
            return current_frame >= self.frame_count
        return False
