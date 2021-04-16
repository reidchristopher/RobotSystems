from motor_controller import MotorController
import time

def forward_and_backward(controller, angle):
    print("Moving forward and back at %.2d degree angle" % angle)
    speed = 50
    t = 1.5
    
    controller.set_dir_servo_angle(angle)
    time.sleep(0.5)
    
    controller.forward(speed)
    time.sleep(t)
    
    controller.backward(speed)
    time.sleep(t)
    controller.stop()
    
def parallel_park(controller, direction):
    print("Doing parallel park in %s direction" % direction)
    
    speed = 50
    angle_sign = -1 if direction == "l" else 1
    
    controller.set_dir_servo_angle(0.0)
    time.sleep(0.5)
    
    controller.forward(speed)
    time.sleep(1.0)
    controller.stop()
    
    controller.set_dir_servo_angle(angle_sign * 20.0)
    controller.backward(speed)
    time.sleep(1.0)
    
    controller.set_dir_servo_angle(-angle_sign * 20.0)
    controller.backward(speed)
    time.sleep(1.0)
    controller.stop()
    
    controller.set_dir_servo_angle(0.0)
    time.sleep(0.5)
    
    controller.forward(speed)
    time.sleep(0.75)
    controller.stop()
    
def three_point_turn(controller, direction):
    print("Doing k turn in %s direction" % direction)
    
    speed = 50
    angle_sign = -1 if direction == "l" else 1
    
    controller.set_dir_servo_angle(angle_sign * 30.0)
    time.sleep(0.1)
    
    controller.forward(speed)
    time.sleep(1.0)
    controller.stop()
    
    controller.set_dir_servo_angle(-angle_sign * 30.0)
    time.sleep(0.1)
    
    controller.backward(speed)
    time.sleep(1.0)
    controller.stop()
    
    controller.set_dir_servo_angle(angle_sign * 30.0)
    time.sleep(0.1)
    
    controller.forward(speed)
    time.sleep(1.0)
    controller.stop()
    
def main():
    
    controller = MotorController()
    
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

            forward_and_backward(controller, angle)
        else:
            direction = ""
            while direction != "l" and direction != "r":
                direction = input("Maneuver (l)eft or (r)ight? ")
                
            if command == "p":
                parallel_park(controller, direction)
            elif command == "k":
                three_point_turn(controller, direction)
    
if __name__ == "__main__":
    main()
