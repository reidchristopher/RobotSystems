from perception import Perception
from motion import Motion
import math
import Camera
import atexit
import cv2

class VisualServo:
    
    def __init__(self):
        
        self.perception = Perception()
        self.motion = Motion()
        
        self.perception.target_color = ('red', 'green', 'blue')
        
        self.camera = Camera.Camera()
        self.camera.camera_open()
        
        atexit.register(self.camera.camera_close)
        
        self.targets_found = []
        
    def scan(self, start_angle, end_angle, num_scans):
        
        start_angle *= math.pi / 180.0
        end_angle *= math.pi / 180.0
        
        radius = 15
        arm_z = 12.5
        
        interval = (end_angle - start_angle) / (num_scans - 1)
        for i in range(num_scans):
            
            angle = start_angle + i * interval
            
            angle += math.pi / 2
            
            arm_x = radius * math.cos(angle)
            arm_y = radius * math.sin(angle)
            
            if not self.motion.init_move(arm_x, arm_y, arm_z):
                raise Exception("Problematic move in scan. Coordinates (%.3f, %.3f, %.3f)" % (arm_x, arm_y, arm_z))
            
            img = self.camera.frame
            display_img = img.copy()
            world_x, world_y, rotation_angle, color = self.perception.get_block_location(display_img)
            cv2.imshow('Frame', display_img)
            
            if not world_x is None:
                # do something interesting
                pass
            
if __name__ == "__main__":
    
    vs = VisualServo()
    
    vs.scan(-90, 90, 8)