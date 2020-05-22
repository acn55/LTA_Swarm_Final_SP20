# import l293d.driver as l293d
# import time
# import RPi.GPIO as GPIO
# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)

# motor1 = l293d.DC(22,18,16)
# try:
    # while True:
        # motor1.clockwise()
        # time.sleep(1)
# except KeyboardInterrupt:
    # print("Crtl C")
    # GPIO.cleanup()
    # l293d.cleanup()
    
    
    
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(22,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)
pwm=GPIO.PWM(22,100)
pwm.start(0)
GPIO.output(18,GPIO.LOW)
GPIO.output(16,GPIO.HIGH)
GPIO.output(22,True)

try:
    while True:
        #forward
        
        pwm.ChangeDutyCycle(75)
        time.sleep(5)
        pwm.ChangeDutyCycle(10)
        print('ok') 
        time.sleep(5)
        GPIO.output(22,False)
        GPIO.output(16,GPIO.LOW)
        GPIO.output(18,GPIO.HIGH)
        GPIO.output(22,True)
        time.sleep(15)
        print('ok') 
        # GPIO.output(channel[2],True)
        # GPIO.output(channel[1],False)
        # pwm.ChangeDutyCycle(75)
        # GPIO.output(channel[0],False)
        # time.sleep(1)
         

except KeyboardInterrupt:
    print("Crtl C pressed")
    GPIO.cleanup()
    pwm.stop()
    

    
