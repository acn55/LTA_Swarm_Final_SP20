# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
# allow the camera to warmup
time.sleep(0.1)
while True:
    camera.capture('/home/pi/Desktop/image.jpg')
    test1 =cv2.imread('/home/pi/Desktop/image.jpg')
    gray=cv2.cvtColor(test1, cv2.COLOR_BGR2GRAY)
    cv2.imshow('image',gray)
    cv2.waitKey(5)
    print("0")




