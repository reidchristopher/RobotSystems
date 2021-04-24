from steering_controller import SteeringController
from motor_controller import MotorController
import time

import cv2
import numpy as np
import numpy.matlib

class ImageSensor:
    
    def __init__(self):
        
        self.camera = cv2.VideoCapture(0)
        
    def get_image(self):
        
        _, image = self.camera.read()
        
        return image

class ImageInterpreter:
    
    def __init__(self):
        
        self.lower_blue = np.array([60, 80, 80])
        self.upper_blue = np.array([150, 255, 255])
    
    def get_position(self, image):
        
        
        x_size = image.shape[1]
        y_size = image.shape[0]
        
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        
        crop = np.zeros_like(mask)
        crop[y_size//2:, :] = 255
        
        cropped = cv2.bitwise_and(mask, crop)

        x_vals = np.linspace(-1, 1, num=x_size)
        x_vals = numpy.matlib.repmat(x_vals, y_size, 1)

        final_mask = cropped == 255

        return np.sum(x_vals * final_mask) / np.sum(final_mask) if np.sum(final_mask) > 0 else 0

def follow_line():
    
    sensor = ImageSensor()
    interpreter = ImageInterpreter()
    steering_controller = SteeringController(p_gain=30)
    
    motor_controller = MotorController()
    
    while True:
        
        # move forward
        motor_controller.forward(20)

        # get sensor values
        image = sensor.get_image()

        # interpret sensor values
        line_position = interpreter.get_position(image)
        print("Line position", line_position)
        
        # adjust steering
        steering_angle = steering_controller.adjust_steering(line_position)
        
        # pause for a short time
        time.sleep(0.05)
        
        
if __name__ == "__main__":
    follow_line()
