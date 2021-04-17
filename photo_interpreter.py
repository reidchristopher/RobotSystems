import numpy as np
    
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