from perception import Perception
from motion import Motion
import math
import Camera
import atexit
import cv2
import time
import numpy as np

class VisualServo:
    
    def __init__(self):
        
        self.perception = Perception()
        self.motion = Motion()
        
        self.perception.target_color = ('red', 'green', 'blue')
        
        self.camera = Camera.Camera()
        self.camera.camera_open()
        
        atexit.register(self.camera.camera_close)
        
        self.targets_not_found = ['red', 'green', 'blue']
        self.targets = dict()
        
    def apply_calibration(self, x, y):
        
        x_coeffs = np.array([0.118, -0.22473, -3.847e-3, -4.792e-3, 3.1361e-5, -7.524e-4, -0.071])
        y_coeffs = np.array([-4.382, -0.1806, 0.20883, 1.345e-3, -3.394e-3, 2.239e-3, 46.115])
        
        x2 = x**2
        x3 = x**3
        
        y2 = y**2
        y3 = y**3
        
        variables = [y, x, y2, x2, y3, x3, 1]
        
        cal_x = np.sum(x_coeffs * variables)
        cal_y = np.sum(y_coeffs * variables)
        
        return cal_x, cal_y
        
        
    def scan(self, start_angle, end_angle, num_scans):
        
        start_angle *= math.pi / 180.0
        end_angle *= math.pi / 180.0
        
        radius = 8
        arm_z = 8
        
        all_found = False
        interval = (end_angle - start_angle) / (num_scans - 1)
        for i in range(num_scans):
            
            angle = start_angle + i * interval
            
            angle += math.pi / 2
            
            arm_x = radius * math.cos(angle)
            arm_y = radius * math.sin(angle)
            
            if not self.motion.init_move(arm_x, arm_y, arm_z):
                raise Exception("Problematic move in scan. Coordinates (%.3f, %.3f, %.3f)" % (arm_x, arm_y, arm_z))
            
            time.sleep(0.5)
            img = self.camera.frame
            height,width=img.shape[:2]

            start_row,start_col=int(width*0.25),int(height*0.25)
            end_row,end_col=int(width*0.75),int(height*0.75)
            
            cropped=img[start_row:end_row,start_col:end_col]
            
            world_x, world_y, rotation_angle, color = self.perception.get_block_location(cropped)
            cv2.imshow('Frame', cropped)
            key = cv2.waitKey(1)
            if key == 27:
                break
            
            if not world_x is None:
                self.perception.target_color = (color,)
                avg_x = 0
                avg_y = 0
                avg_rotation = 0
                num_to_avg = 10
                for scan in range(num_to_avg):
                    time.sleep(0.2)
                    img = self.camera.frame
                    world_x, world_y, rotation_angle, color = self.perception.get_block_location(img)
                    if world_x is None:
                        continue
                    avg_x += world_x / num_to_avg
                    avg_y += world_y / num_to_avg
                    avg_rotation += rotation_angle / num_to_avg
                    
                actual_x, actual_y = self.apply_calibration(avg_x, avg_y)
                
                angle -= math.pi / 2
                rotated_x = actual_x * math.cos(angle) - actual_y * math.sin(angle)
                rotated_y = actual_x * math.sin(angle) + actual_y * math.cos(angle)
                
                self.targets_not_found.remove(color)
                self.targets[color] = (rotated_x, rotated_y, avg_rotation)
                
                self.perception.target_color = self.targets_not_found
                
                if len(self.targets_not_found) == 0:
                    all_found = True
                    
            if all_found:
                break
            
        red_x, red_y, red_rotation = self.targets['red']
        place_z = 1.5
        for color in ['green', 'blue']:
            place_z += 2.5
            
            x, y, rotation = self.targets[color]
            
            self.motion.init_move(x, y)
            self.motion.pick(x, y, 1.5, rotation)
            self.motion.place(red_x, red_y, place_z, red_rotation)
                    
            
if __name__ == "__main__":
    
    num_scans = 12
    
    import sys
    if len(sys.argv) == 2: 
        num_scans = int(sys.argv[1])
    
    vs = VisualServo()
    
    vs.scan(-90, 90, num_scans)
    
    # while True:
    #     vs.scan(0, 0, 200)