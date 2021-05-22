from picarx_improved import *
import time

def main():
    
    set_dir_servo_angle(0.0)
    time.sleep(1)
    forward(100)
    time.sleep(1)
    stop()

if __name__ == "__main__":
    main()