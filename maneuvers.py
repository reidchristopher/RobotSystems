from picarx_improved import *

def forward_and_backward(angle):
    print("Moving forward and back at %.2d degree angle" % angle)
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
    print("Doing parallel park in %s direction" % direction)
    
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
    print("Doing k turn in %s direction" % direction)
    
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
    
    def input_is_valid(i):
        return i == "f" or i == "p" or i =="k" or i == "q"
    
    
    while True:
        command = ""
        while not input_is_valid(command):
            command = input("--------------------------------------------\n"
                            "What would you like the car to do?\n"
                            "Move (f)orward and backwards?\n"
                            "Do a (p)arallel parking maneuver?\n"
                            "Make a (k)-turn?\n" 
                            "\n"
                            "(f, p, or k for motion, q to quit)\n"
                            "--------------------------------------------\n")
            command = command.lower()
            
            
        if command == "q":
            break
        elif command == "f":
            limit = 45
            err_str = "Please enter a valid number between %d and %d" % (-limit, limit)
            angle = None
            while angle is None:
                try:
                    angle = float(input("Enter desired steering angle: "))
                    if abs(angle) > limit:
                        angle = None
                        print(err_str)
                except ValueError:
                    print(err_str)

            forward_and_backward(angle)
        else:
            direction = ""
            while direction != "l" and direction != "r":
                direction = input("Maneuver (l)eft or (r)ight? ")
                
            if command == "p":
                parallel_park(direction)
            elif command == "k":
                three_point_turn(direction)
    
if __name__ == "__main__":
    main()
