from photo_sensor import PhotoSensor
from photo_interpreter import PhotoInterpreter
from photo_steering_controller import PhotoSteeringControl
from motor_controller import MotorController
import time

def follow_line():
    
    sensor = PhotoSensor()
    interpreter = PhotoInterpreter(sensitivity=5e-3, polarity=1)
    steering_controller = PhotoSteeringControl(p_gain=30)
    
    motor_controller = MotorController()
    
    while True:
        
        # move forward
        motor_controller.forward(20)
        
        # get sensor values
        adc_values = sensor.get_adc_values()
        
        # interpret sensor values
        line_position = interpreter.get_position(adc_values)
        print("Line position", line_position)
        
        # adjust steering
        steering_angle = steering_controller.adjust_steering(line_position)
        
        
        # pause for a short time
        time.sleep(0.1)
        
        
if __name__ == "__main__":
    follow_line()