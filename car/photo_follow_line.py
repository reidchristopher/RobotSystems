try :
    from ezblock import *
    import sys
    sys.path.append(r'/opt/ezblock')
    from ezblock import __reset_mcu__
    __reset_mcu__()
    time.sleep(0.01)
except ImportError :
    print (""" This computer does not appear to be a PiCar - X system
    (/ opt / ezblock is not present ) . Shadowing hardware calls
    with substitute functions """)
    from sim_ezblock import *

from steering_controller import SteeringController
from motor_controller import MotorController
import time

import numpy as np

class PhotoSensor:
    
    def __init__(self):
        
        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')
        
    def get_adc_values(self):
        adc_value_list = []
        adc_value_list.append(self.S0.read())
        adc_value_list.append(self.S1.read())
        adc_value_list.append(self.S2.read())
        return adc_value_list
    
class PhotoInterpreter:
    
    def __init__(self, sensitivity=5e-3, polarity=1):
        
        # positive polarity for brighter line, negative polarity for darker line
        if polarity != 1 and polarity != -1:
            raise ValueError("PhotoInterpreter polarity must equal +1 or -1")
        
        self.sensitivity = sensitivity
        self.polarity = polarity
        
    # return in range [-1, 1], positive for 
    def get_position(self, adc_outputs):
        
        # low values -> low brightness
        # 0, 1, 2 -> left, middle, right
        
        # if darker line than background -> darker means closer to line
        # if lighter line than background -> lighter means closer to line
        diffs = np.array(adc_outputs[0:2]) - np.array(adc_outputs[1:3])
        diffs *= self.polarity
        
        if np.argmax(diffs) == 0:
            side = -1
        else:
            side = 1
        
        # positive value means line is to the right
        value = np.max(diffs) * self.sensitivity * side
        
        value = np.clip(value, -1, 1)
        
        return value

def follow_line():
    
    sensor = PhotoSensor()
    interpreter = PhotoInterpreter(sensitivity=5e-3, polarity=1)
    steering_controller = SteeringController(p_gain=30)
    
    motor_controller = MotorController()
    
    while True:
        
        # move forward
        motor_controller.forward(20)
        
        # get sensor values
        adc_values = sensor.get_adc_values()
        
        # interpret sensor values
        line_position = interpreter.get_position(adc_values)
        print("Line position: %.2f" % line_position)
        
        # adjust steering
        steering_angle = steering_controller.adjust_steering(line_position)
        
        # pause for a short time
        time.sleep(0.1)
        
        
if __name__ == "__main__":
    follow_line()
