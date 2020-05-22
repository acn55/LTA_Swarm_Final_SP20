import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

channel1=[38,36,40] #right
channel2=[32,31,29] #bottom
channel3=[33,37,35] #left
GPIO.setup(channel1,GPIO.OUT)
GPIO.setup(channel2,GPIO.OUT)
GPIO.setup(channel3,GPIO.OUT)
#LED
GPIO.setup(22,GPIO.OUT)
pwm=GPIO.PWM(22,10) 
pwm.start(10)

#set the initial logic output
def right():
    GPIO.output(channel1[0],GPIO.HIGH)
    GPIO.output(channel1[1],GPIO.LOW)
    GPIO.output(channel1[2],GPIO.HIGH)
    GPIO.output(channel3[2],GPIO.LOW)
def left():
    GPIO.output(channel3[1],GPIO.HIGH)
    GPIO.output(channel3[0],GPIO.LOW)
    GPIO.output(channel3[2],GPIO.HIGH)
    GPIO.output(channel1[2],GPIO.LOW)
def top():
    GPIO.output(channel2[0],GPIO.HIGH)
    GPIO.output(channel2[1],GPIO.LOW)
    GPIO.output(channel2[2],GPIO.HIGH)
    GPIO.output(channel1[2],GPIO.LOW)
    GPIO.output(channel3[2],GPIO.LOW)
def bot():
    GPIO.output(channel2[1],GPIO.HIGH)
    GPIO.output(channel2[0],GPIO.LOW)
    GPIO.output(channel2[2],GPIO.HIGH)
    GPIO.output(channel1[2],GPIO.LOW)
    GPIO.output(channel3[2],GPIO.LOW)
def forward():
    GPIO.output(channel1[0],GPIO.HIGH)
    GPIO.output(channel1[1],GPIO.LOW)
    GPIO.output(channel1[2],GPIO.HIGH)
    GPIO.output(channel3[1],GPIO.HIGH)
    GPIO.output(channel3[0],GPIO.LOW)
    GPIO.output(channel3[2],GPIO.HIGH)
def backward():
    GPIO.output(channel1[1],GPIO.HIGH)
    GPIO.output(channel1[0],GPIO.LOW)
    GPIO.output(channel1[2],GPIO.HIGH)
    GPIO.output(channel3[0],GPIO.HIGH)
    GPIO.output(channel3[1],GPIO.LOW)
    GPIO.output(channel3[2],GPIO.HIGH)
def stopmotor():
    GPIO.output(channel1[2],GPIO.LOW)
    GPIO.output(channel2[2],GPIO.LOW)
    GPIO.output(channel3[2],GPIO.LOW)
def quitserver():
    GPIO.cleanup()
    pwm.stop()
    
if __name__ == '__main__':    
    try:
        while True:
            command =input("input:")
            if command == 'a': #turn left
                left()
            if command == 'd': #turn right
                right()
            if command == 'w': #turn forward
                forward()
            if command == 's': #turn backward
                backward()
            if command == 'u': #turn top
                top()
            if command == 'i': #turn down
                bot()
            if command == 'q': #stop motor
                stopmotor()    
            
    except KeyboardInterrupt:
        print("Crtl C pressed")
        GPIO.cleanup()
        pwm.stop()
        
