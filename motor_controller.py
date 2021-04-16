try :
    from ezblock import *
except ImportError :
    print (""" This computer does not appear to be a PiCar - X system
    (/ opt / ezblock is not present ) . Shadowing hardware calls
    with substitute functions """)
    from sim_ezblock import *
import math
import time
import atexit


class MotorController:
    
    def __init__(self):
                
        self.PERIOD = 4095
        self.PRESCALER = 10
        self.TIMEOUT = 0.02

        self.steering_servo_pin = Servo(PWM('P2'))
        self.camera_servo_pin1 = Servo(PWM('P0'))
        self.camera_servo_pin2 = Servo(PWM('P1'))
        self.left_rear_pwm_pin = PWM("P13")
        self.right_rear_pwm_pin = PWM("P12")
        self.left_rear_dir_pin = Pin("D4")
        self.right_rear_dir_pin = Pin("D5")

        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')

        self.Servo_dir_flag = 1
        self.servo_angle = 0
        self.dir_cal_value = 7
        self.cam_cal_value_1 = 0
        self.cam_cal_value_2 = 0
        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]
        self.cali_dir_value = [1, -1]
        self.cali_speed_value = [0, 0]
        
        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)
            
        atexit.register(self.cleanup)

    def set_motor_speed(self, motor, speed):
        motor -= 1
        if speed >= 0:
            direction = 1 * self.cali_dir_value[motor]
        elif speed < 0:
            direction = -1 * self.cali_dir_value[motor]
        speed = abs(speed)
        speed = speed - self.cali_speed_value[motor]
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    def motor_speed_calibration(self, value):
        self.cali_speed_value = value
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(self.cali_speed_value)
        else:
            self.cali_speed_value[0] = abs(self.cali_speed_value)
            self.cali_speed_value[1] = 0

    def motor_direction_calibration(self, motor, value):
        # 0: positive direction
        # 1: negative direction
        motor -= 1
        if value == 1:
            self.cali_dir_value[motor] = -1*self.cali_dir_value[motor]

    def steering_servo_angle_calibration(self, value):
        self.dir_cal_value = value
        self.set_steering_angle(self.dir_cal_value)

    def set_steering_angle(self, value):
        self.servo_angle = value+self.dir_cal_value
        self.steering_servo_pin.angle(value+self.dir_cal_value)

    def camera_servo1_angle_calibration(self, value):
        self.cam_cal_value_1 = value
        self.set_camera_servo1_angle(self.cam_cal_value_1)

    def camera_servo2_angle_calibration(self, value):
        self.cam_cal_value_2 = value
        self.set_camera_servo2_angle(self.cam_cal_value_2)

    def set_camera_servo1_angle(self, value):
        self.camera_servo_pin1.angle(-1 *(value+self.cam_cal_value_1))

    def set_camera_servo2_angle(self, value):
        self.camera_servo_pin2.angle(-1 * (value+self.cam_cal_value_2))

    def get_adc_value(self):
        adc_value_list = []
        adc_value_list.append(self.S0.read())
        adc_value_list.append(self.S1.read())
        adc_value_list.append(self.S2.read())
        return adc_value_list

    def set_power(self, speed):
        self.set_motor_speed(1, speed)
        self.set_motor_speed(2, speed) 

    def backward(self, speed):
        self.forward(-speed)

    def forward(self, speed):
        d = 3.75
        a = 2.25

        if self.servo_angle == 0.0:
            self.set_motor_speed(1, -1*speed)
            self.set_motor_speed(2, -1*speed)
        else:
            if self.servo_angle > 0.0:
                inner_wheel = 1
                outer_wheel = 2
            else:
                inner_wheel = 2
                outer_wheel = 1
                
            angle = abs(self.servo_angle)
            r = d / math.sin(math.radians(angle))
            ri = r - a * (2 - math.cos(math.radians(angle)))
            ro = ri + 2 * a
            
            vi = ri / r * speed
            vo = ro / r * speed
            
            self.set_motor_speed(inner_wheel, -1*vi)
            self.set_motor_speed(outer_wheel, -1*vo)

    def stop(self):
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)

    def cleanup(self):
        self.stop()