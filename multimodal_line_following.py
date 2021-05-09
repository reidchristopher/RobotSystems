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
import numpy as np

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
    
    def __init__(self, controller, p_gain):
        
        self.p_gain = p_gain
        
        self.controller = controller
        
    def adjust_steering(self, line_position_value):
        
        steering_angle = self.p_gain * line_position_value
        
        self.controller.set_steering_angle(steering_angle)
        
        return steering_angle
    
class DistanceSensor:
    
    def __init__(self):
        
        self.sensor = Ultrasonic(Pin("D0"), Pin("D1"))
    
    def get_distance(self):
        
        return self.sensor.read()
    
class DistanceInterpreter:
    
    # distance threshold is distance under which the car stops (in cm)
    def __init__(self, dist_threshold):
        
        self.dist_threshold = dist_threshold
        
    def is_object_close(self, dist):
        
        return dist < self.dist_threshold and dist > 0
    
class SpeedController:
    
    def __init__(self, controller):
        
        self.controller = controller
    
    def adjust_speed(self, object_close):
        lock = Lock()
        with lock:
            if object_close:
                self.controller.stop()
            else:
                self.controller.forward(20)

def follow_line():

    # create timer bus and producer
    timer_bus = rossros.Bus(initial_message=False)
    timer = rossros.Timer(timer_bus, duration=5, delay=0.25, termination_busses=timer_bus, name="Termination Timer")
    
    # create controller class for motor functions
    motor_controller = MotorController()
    
    # create photo sensor, interpreter, controller items, busses, and producer, consumer-producer, consumer items
    photo_sensor = PhotoSensor()
    photo_interpreter = PhotoInterpreter(sensitivity=3e-3)
    steering_controller = SteeringController(motor_controller, p_gain=30)
    
    photo_sensor_bus = rossros.Bus()
    photo_interpretation_bus = rossros.Bus()
    
    photo_sensor_producer = rossros.Producer(photo_sensor.get_adc_values, photo_sensor_bus, delay=0.05, termination_busses=timer_bus, name="Photo Sensor Producer")
    photo_interpretation_consumer_producer = rossros.ConsumerProducer(photo_interpreter.get_position, photo_sensor_bus, photo_interpretation_bus, 
                                                                      delay=0.05, termination_busses=timer_bus, name="Photo Interpretation Consumer-Producer")
    steering_controller_consumer = rossros.Consumer(steering_controller.adjust_steering, photo_interpretation_bus, delay=0.1, termination_busses=timer_bus,
                                           name="Steering controller consumer")
    
    # create distance sensor, interpreter, controller items, busses, and producer, consumer-producer, consumer items
    distance_sensor = DistanceSensor()
    distance_interpreter = DistanceInterpreter(5) # 5 cm stopping distance
    speed_controller = SpeedController(motor_controller)
    
    distance_sensor_bus = rossros.Bus()
    distance_interpretation_bus = rossros.Bus()
    
    distance_sensor_producer = rossros.Producer(distance_sensor.get_distance, distance_sensor_bus, delay=0.1, termination_busses=timer_bus, 
                                                name="Distance Sensor Producer")
    distance_interpretation_consumer_producer = rossros.ConsumerProducer(distance_interpreter.is_object_close, distance_sensor_bus, distance_interpretation_bus,
                                                                         delay=0.1, termination_busses=timer_bus, name="Distance Interpretation Consumer Producer")
    speed_controller_consumer = rossros.Consumer(speed_controller.adjust_speed, distance_interpretation_bus, delay=0.1, termination_busses=timer_bus,
                                                   name="Speed controller consumer")
    
    # execute threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        # start steering control threads
        e_photo_sensor = executor.submit(photo_sensor_producer)
        e_photo_interpreter = executor.submit(photo_interpretation_consumer_producer)
        e_steering_controller = executor.submit(steering_controller_consumer)
        
        # starts speed control (braking or not) threads
        e_distance_sensor = executor.submit(distance_sensor_producer)
        e_distance_interpreter = executor.submit(distance_interpretation_consumer_producer)
        e_speed_controller = executor.submit(speed_controller_consumer)
        
        # start termination timer thread
        e_timer = executor.submit(timer)
    
        
if __name__ == "__main__":
    follow_line()
