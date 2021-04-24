from motor_controller import MotorController
    
class ImageSteeringControl:
    
    def __init__(self, p_gain):
        
        self.p_gain = p_gain
        
        self.controller = MotorController()
        
    def adjust_steering(self, line_position_value):
        
        steering_angle = self.p_gain * line_position_value
        
        self.controller.set_steering_angle(steering_angle)
        
        return steering_angle
