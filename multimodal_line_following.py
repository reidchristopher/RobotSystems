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

from motor_controller import MotorController
import time

import cv2
import numpy as np
import numpy.matlib

import concurrent.futures
from threading import Lock

import rossros

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
            
class SteeringController:
    
    def __init__(self, p_gain):
        
        self.p_gain = p_gain
        
        self.controller = MotorController()
        
    def adjust_steering(self, line_position_value):
        
        steering_angle = self.p_gain * line_position_value
        
        self.controller.set_steering_angle(steering_angle)
        
        return steering_angle

def follow_line():
    
    timer_bus = rossros.Bus(initial_message=False)
    timer = rossros.Timer(timer_bus, duration=5, termination_busses=timer_bus, name="Termination Timer")
    
    sensor = PhotoSensor()
    interpreter = PhotoInterpreter()
    steering_controller = SteeringController(p_gain=30)
    
    sensor_value_bus = rossros.Bus()
    interpretation_value_bus = rossros.Bus()
    
    sensor_producer = rossros.Producer(sensor.get_adc_values, sensor_value_bus, termination_busses=timer_bus, name="Sensor Producer")
    interpretation_consumer_producer = rossros.ConsumerProducer(interpreter.get_position, sensor_value_bus, interpretation_value_bus, 
                                                                termination_busses=timer_bus, name="Interpretation Consumer-Producer")
    controller_consumer = rossros.Consumer(steering_controller.adjust_steering, interpretation_value_bus, termination_busses=timer_bus, 
                                           name="Steering controller consumer")
    
    motor_controller = MotorController()
    
    # move forward
    motor_controller.forward(20)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        e_sensor = executor.submit(sensor_producer)
        e_interpreter = executor.submit(interpretation_consumer_producer)
        e_controller = executor.submit(controller_consumer)
        
        e_timer = executor.submit(timer)
    
        
if __name__ == "__main__":
    follow_line()
