from Image_sensor import ImageSensor
from Image_interpreter import ImageInterpreter
from Image_steering_controller import ImageSteeringControl
from motor_controller import MotorController
import time

def follow_line():
    
    sensor = ImageSensor()
    interpreter = ImageInterpreter()
    steering_controller = ImageSteeringControl(p_gain=30)
    
    motor_controller = MotorController()
    
    while True:
        
        # move forward
        motor_controller.forward(20)
        
        # get sensor values
        adc_values = sensor.get_image()
        
        # interpret sensor values
        line_position = interpreter.get_position(image)
        print("Line position", line_position)
        
        # adjust steering
        steering_angle = steering_controller.adjust_steering(line_position)
        
        # pause for a short time
        time.sleep(0.05)
        
        
if __name__ == "__main__":
    follow_line()