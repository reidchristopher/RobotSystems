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

class MessageBus:
    
    def __init__(self, label):
        self.label = label
        self.message = None
    
    def write(self, value):
        self.message = value
        
    def read(self):
        return self.message

class PhotoSensorProducer:
    
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
    
    def run(self, output_bus, delay):
        lock = Lock()
        while True:
            
            with lock:
                values = self.get_adc_values()
            
            output_bus.write(self.get_adc_values())
            
            time.sleep(delay)

class PhotoInterpreterConsumerProducer:
    
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
    
    def run(self, input_bus, output_bus, delay):
        
        while True:
            
            image = input_bus.read()
            
            output_bus.write(self.get_position(image))
            
            time.sleep(delay)
            
class SteeringControllerConsumer:
    
    def __init__(self, p_gain):
        
        self.p_gain = p_gain
        
        self.controller = MotorController()
        
    def adjust_steering(self, line_position_value):
        
        steering_angle = self.p_gain * line_position_value
        
        self.controller.set_steering_angle(steering_angle)
        
        return steering_angle
    
    def run(self, input_bus, delay):
        
        while True:
            
            line_position = input_bus.read()
            
            self.adjust_steering(line_position)
            
            time.sleep(delay)

def follow_line():
    
    sensor = PhotoSensorProducer()
    interpreter = PhotoInterpreterConsumerProducer()
    steering_controller = SteeringControllerConsumer(p_gain=30)
    
    sensor_value_bus = MessageBus("sensor_values")
    interpretation_value_bus = MessageBus("interpretation_value")
    
    motor_controller = MotorController()
    
    sensor_delay = 0.01
    interpreter_delay = 0.02
    controller_delay = 0.5
    
    # move forward
    motor_controller.forward(20)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        e_sensor = executor.submit(sensor.run, sensor_value_bus, sensor_delay)
        e_interpreter = executor.submit(interpreter.run, sensor_value_bus, interpretation_value_bus, interpreter_delay)
        e_controller = executor.submit(steering_controller.run, interpretation_value_bus, controller_delay)
    
        
if __name__ == "__main__":
    follow_line()
