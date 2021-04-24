import cv2

class ImageSensor:
    
    def __init__(self):
        
        self.camera = cv2.VideoCapture(0)
        
    def get_image(self):
        
        _, image = self.camera.read()
        
        return image