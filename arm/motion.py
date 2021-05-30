#!/usr/bin/python3
# coding=utf8
import sys

sys.path.append('/home/pi/ArmPi/')
import cv2
import time
from ArmIK.Transform import getAngle
from ArmIK.ArmMoveIK import ArmIK
import HiwonderSDK.Board as Board
import atexit

class Motion:
    
    def __init__(self):
        
        self.AK = ArmIK()
        self.servo1 = 500
        self.base_z = 1.5
        self.block_height = 2.5
        self.num_stacked = 0
        
        self.coordinates = {
        'red':    (-15 + 0.5, 12 - 0.5, 1.5),
        'green':  (-15 + 0.5, 6 - 0.5,  1.5),
        'blue':   (-15 + 0.5, 0 - 0.5,  1.5),
        'pallet': (-15 + 1, -7 - 0.5, 1.5),
        }

        atexit.register(self.reset)
        
    def sort(self, block_x, block_y, block_rotation, block_color):
        
        if not block_color in ['red', 'green', 'blue']:
            raise Exception("Bad color :(")
        
        place_x, place_y, place_z = self.coordinates[block_color]
        
        if not self.init_move(block_x, block_y):
            return False
        
        self.pick(block_x, block_y, self.base_z, block_rotation)
        
        self.place(place_x, place_y, place_z)
        
        self.reset()

    def palletize(self, block_x, block_y, block_rotation):
        
        place_x, place_y, place_z = self.coordinates["pallet"]
        
        place_z += self.block_height * self.num_stacked
        
        if not self.init_move(block_x, block_y):
            return False
        
        self.pick(block_x, block_y, self.base_z, block_rotation)
        
        self.place(place_x, place_y, place_z)
        
        self.reset()
        self.num_stacked += 1
        self.num_stacked %= 3

    def pick(self, x, y, z, rotation):
        
        servo2_angle = getAngle(x, y, rotation) #计算夹持器需要旋转的角度
        Board.setBusServoPulse(1, self.servo1 - 280, 500)  # 爪子张开
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.5)
        
        self.AK.setPitchRangeMoving((x, y, z), -90, -90, 0, 1000)
        time.sleep(1.5)

        Board.setBusServoPulse(1, self.servo1, 500)  #夹持器闭合
        time.sleep(0.8)

        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((x, y, 12), -90, -90, 0, 1000)  #机械臂抬起
        time.sleep(1)

    def place(self, x, y, z, rotation=-90):
        
        result = self.AK.setPitchRangeMoving((x, y, 12), -90, -90, 0)   
        time.sleep(result[2]/1000)
                        
        servo2_angle = getAngle(x, y, -90)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.5)

        self.AK.setPitchRangeMoving((x, y, z + 3), -90, -90, 0, 500)
        time.sleep(0.5)
                
        self.AK.setPitchRangeMoving((x, y, z), -90, -90, 0, 1000)
        time.sleep(0.8)

        Board.setBusServoPulse(1, self.servo1 - 200, 500)  # 爪子张开  ，放下物体
        time.sleep(0.8)

        self.AK.setPitchRangeMoving((x, y, 12), -90, -90, 0, 800)
        time.sleep(0.8)

    # initial move, returns false if unreachable, otherwise makes initial motion
    def init_move(self, x, y, z=7):
        
        result = self.AK.setPitchRangeMoving((x, y, z), -90, -90, 0)
        if result == False:
            return False
        else:
            # wait for motion to execute
            time.sleep(result[2]/1000) 
            
            return True
        
    # return to default position
    def reset(self):
        Board.setBusServoPulse(1, self.servo1 - 250, 300)
        time.sleep(0.5)
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        time.sleep(0.5)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(1.5)
    
def main():
    
    import sys
    arg_info = "Requires 1 argument for action to take: pick from [sort, palletize]"
    if len(sys.argv) != 2:
        print(arg_info)
        return
    elif not sys.argv[1] in ["sort", "palletize"]:
        print(arg_info)
        return
    if sys.argv[1] != "palletize":
        sort = True
    else:
        sort = False
    
    import Camera
    my_camera = Camera.Camera()
    my_camera.camera_open()

    from perception import Perception
    p = Perception()
    p.target_color = ("red", "blue", "green")
    
    motion = Motion()
    while True:
        img = my_camera.frame
        if img is not None:
            display_img = img.copy()
            world_x, world_y, rotation_angle, color = p.get_block_location(display_img)
            cv2.imshow('Frame', display_img)
            
            key = cv2.waitKey(1)
            if key == 27:
                break
            if world_x is not None:
                if sort:
                    motion.sort(world_x, world_y, rotation_angle, color)
                else:
                    motion.palletize(world_x, world_y, rotation_angle)

    my_camera.camera_close()
    cv2.destroyAllWindows()
    
    
if __name__ == "__main__":
    
    main()
