import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(16,GPIO.OUT)
pwm=GPIO.PWM(16,50)
pwm.start(1)
try:
    while True:
        print("ok")
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
