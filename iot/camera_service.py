import cv2
import time
from datetime import datetime

class CameraService:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        time.sleep(2)  # Camera warm-up
        
    def capture_image(self, save_dir="static/uploads"):
        ret, frame = self.camera.read()
        if ret:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"garment_{timestamp}.jpg"
            filepath = f"{save_dir}/{filename}"
            cv2.imwrite(filepath, frame)
            return filepath
        return None

    def release(self):
        self.camera.release()