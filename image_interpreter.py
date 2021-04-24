import cv2
import numpy as np

class ImageInterpreter:
    
    def __init__(self):
        
        self.lower_blue = np.array([60, 80, 80])
        self.upper_blue = np.array([150, 255, 255])
    
    def get_position(self, image):
        
        
        x_size = image.shape[1]
        y_size = image.shape[0]
        
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        
        edges = cv2.Canny(mask, 200, 400)
        
        crop = np.zeros_like(edges)
        crop[y_size//2:, :] = 255
        
        cropped = cv2.bitwise_and(edges, crop)
        
        x = 0
        y = 0
        count = np.sum(cropped)
        for i, row in enumerate(cropped):
            for j, pixel in enumerate(row):
                x += j / count * pixel
                y += i / count * pixel
                
        return x / x_size - 0.5
        
        # rho = 1  # distance precision in pixel, i.e. 1 pixel
        # angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
        # min_threshold = 10  # minimal of votes
        # line_segments = cv2.HoughLinesP(cropped, rho, angle, min_threshold, 
        #                             np.array([]), minLineLength=8, maxLineGap=4)
        
        # for segment in line_segments:
        #     for x1, y1, x2, y2 in segment:
                
        #         if x1 == x2:
        #             continue
                
        #         slope = np.polyfit((x1, x2), (y1, y2), 1)
                
        
        # return cropped