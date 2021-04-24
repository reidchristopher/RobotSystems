import cv2
from image_sensor import ImageSensor
from image_interpreter import ImageInterpreter

sensor = ImageSensor()
interpreter = ImageInterpreter()

image = sensor.get_image()
interpretation = interpreter.get_lane(image)

cv2.imshow("test", interpretation)

cv2.waitKey(2000)

cv2.destroyAllWindows()