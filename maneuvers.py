from picarx_improved import *

def forward_and_backward(angle):
    speed = 50
    t = 1.5
    
    set_dir_servo_angle(angle)
    time.sleep(0.5)
    
    forward(speed)
    time.sleep(t)
    
    backward(speed)
    time.sleep(t)
    stop()
    
def parallel_park(direction):
    speed = 50
    angle_sign = -1 if direction == "l" else 1
    
    set_dir_servo_angle(0.0)
    time.sleep(0.5)
    
    forward(speed)
    time.sleep(1.0)
    stop()
    
    set_dir_servo_angle(angle_sign * 20.0)
    backward(speed)
    time.sleep(1.0)
    
    set_dir_servo_angle(-angle_sign * 20.0)
    backward(speed)
    time.sleep(1.0)
    stop()
    
    set_dir_servo_angle(0.0)
    time.sleep(0.5)
    
    forward(speed)
    time.sleep(0.75)
    stop()
    
def three_point_turn(direction):
    
    speed = 50
    angle_sign = -1 if direction == "l" else 1
    
    set_dir_servo_angle(angle_sign * 30.0)
    time.sleep(0.1)
    
    forward(speed)
    time.sleep(1.0)
    stop()
    
    set_dir_servo_angle(-angle_sign * 30.0)
    time.sleep(0.1)
    
    backward(speed)
    time.sleep(1.0)
    stop()
    
    set_dir_servo_angle(angle_sign * 30.0)
    time.sleep(0.1)
    
    forward(speed)
    time.sleep(1.0)
    stop()
    
def main():
    
    forward_and_backward(0.0)
    forward_and_backward(30.0)
    forward_and_backward(-30.0)
    
    parallel_park("l")
    parallel_park("r")
    
    three_point_turn("l")
    three_point_turn("r")
    
if __name__ == "__main__":
    main()
