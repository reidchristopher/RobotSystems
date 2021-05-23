#!/usr/bin/python3
# coding=utf8
import sys

sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import threading
from LABConfig import color_range
from ArmIK.Transform import getMaskROI, getROI, getCenter, convertCoordinate
from CameraCalibration.CalibrationConfig import square_length
import numpy as np
import math

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
    
class Perception:
    
    def __init__(self):
        
        self.range_rgb = {
                    'red': (0, 0, 255),
                    'blue': (255, 0, 0),
                    'green': (0, 255, 0),
                    'black': (0, 0, 0),
                    'white': (255, 255, 255)
                    }
        
        self.size = (640, 480)
        self.roi = None
        self.rect = None
        self.count = 0
        self.track = False
        self.get_roi = False
        self.center_list = []
        self.target_color = None
        self.detect_color = None
        self.action_finish = True
        self.rotation_angle = None
        self.last_x, last_y = 0, 0
        self.world_X, world_Y = 0, 0
        self.world_x, world_y = 0, 0
        self.start_count_t1, t1 = True, None
        self.start_pick_up, first_move = False, False
        
    def draw_calibration_lines(self, img):
        
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        
        return img
    
    def resize(self, img):
        
        return cv2.resize(img, self.size, interpolation=cv2.INTER_NEAREST)
    
    def apply_blur(self, img):
        
        return cv2.GaussianBlur(img, (11, 11), 11)
    
    def apply_ROI_mask(self, img):
        
        return getMaskROI(img, self.roi, self.size)
    
    def preprocess_image(self, img):
        
        # resize the image and add gaussian blur
        frame_resize = self.resize(img)
        frame_gb = self.apply_blur(frame_resize)
        
        # if we already detected an object somewhere, we'll only look in that area until we can't find it anymore
        if self.get_roi and self.start_pick_up:
            self.get_roi = False
            frame_gb = self.apply_ROI_mask(frame_gb) 
        
        # convert RGB to Lab
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)
        
        return frame_lab
    
    def find_largest_area(self, img, color):
    
        # helper function for finding the largest area given contours
        def getAreaMaxContour(contours):
            contour_area_temp = 0
            contour_area_max = 0
            area_max_contour = None

            for c in contours: 
                contour_area_temp = math.fabs(cv2.contourArea(c))  
                if contour_area_temp > contour_area_max:
                    contour_area_max = contour_area_temp
                    if contour_area_temp > 300: 
                        area_max_contour = c

            return area_max_contour, contour_area_max
        
        frame_mask = cv2.inRange(img, color_range[color][0], color_range[color][1])  # find part of image in the color's range
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # erosion then dilation -> remove external noise
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # dilation then erosion -> close internal holes
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # find outlines
        areaMaxContour, area_max = getAreaMaxContour(contours)  # find the largest contour
        
        return areaMaxContour, area_max
    
    def get_world_location(self, contour, display_img=None):
        
        rect = cv2.minAreaRect(contour)
        box = np.int0(cv2.boxPoints(rect))

        self.roi = getROI(box) # get the area of the region of interest
        self.get_roi = True

        img_centerx, img_centery = getCenter(rect, self.roi, self.size, square_length)  # get the center of the box
        world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size) # convert from image to world coordinates
        
        if display_img is not None:
             # draw contour
            cv2.drawContours(display_img, [box], -1, self.range_rgb[self.detect_color], 2)
            
            # draw center point
            cv2.putText(display_img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[self.detect_color], 1) 
        
        return world_x, world_y
        
    def run(self, img):
        
        # make a copy of the image and draw calibration lines
        img_copy = img.copy()
        self.draw_calibration_lines(img)
        
        # preprocess the image
        img_lab = self.preprocess_image(img_copy)
        
        area_max = 0
        areaMaxContour = 0
        self.detect_color = "None"
        draw_color = "black"
        if not self.start_pick_up:
            for color in color_range:
                if color in self.target_color:
                    areaMaxContour, area_max = self.find_largest_area(img_lab, color)
                    
                    # maximize over the different colors
                    if areaMaxContour is not None:
                        if area_max > max_area:
                            max_area = area_max
                            self.detect_color = color
                            draw_color = color
                            areaMaxContour_max = areaMaxContour
            if area_max > 2500:  # check if the area is large enough to indicate we found a block
                world_x, world_y = self.get_world_location(areaMaxContour_max, display_img=img)
                
                cv2.putText(img, "Color: " + self.detect_color, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, draw_color, 2)
                
                # distance = math.sqrt(pow(world_x - self.last_x, 2) + pow(world_y - self.last_y, 2)) # see if the object has moved since last time
                # self.last_x, self.last_y = world_x, world_y
                # self.track = True
                # # print(count,distance)
                
                # # make the final decision about whether to move
                # if self.action_finish:
                #     if distance < 0.3: # if the object has not moved very far, add location to list
                #         self.center_list.extend((world_x, world_y))
                #         self.count += 1
                #         if self.start_count_t1:
                #             self.start_count_t1 = False
                #             t1 = time.time()
                #         # if the object has stayed tracked for over a second and a half, start pickup
                #         if time.time() - t1 > 1.5: 
                #             self.rotation_angle = rect[2]
                #             self.start_count_t1 = True
                #             self.world_X, self.world_Y = np.mean(np.array(self.center_list).reshape(self.count, 2), axis=0)
                #             self.count = 0
                #             self.center_list = []
                #             self.start_pick_up = True
                #     else: # if object has moved, restart location list
                #         t1 = time.time()
                #         self.start_count_t1 = True
                #         self.count = 0
                #         self.center_list = []
        return img
    
def main():
    
    import Camera
    my_camera = Camera.Camera()
    my_camera.camera_open()
    perception = Perception()
    perception.target_color = ("red", "blue", "green")
    while True:
        img = my_camera.frame
        if img is not None:
            img_copy = img.copy()
            display_img = perception.run(img_copy)
            cv2.imshow('Frame', display_img)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    
    main()
