import time 
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(17,GPIO.OUT) #AIN2
GPIO.setup(18,GPIO.OUT) #AIN1


#set the initial logic output
def cw():
	GPIO.output(17,GPIO.LOW)
	GPIO.output(18,GPIO.HIGH)
def ccw():
	GPIO.output(17,GPIO.HIGH)
	GPIO.output(18,GPIO.LOW)
	
	



count = 0
keep_going = True
keep = False
try:
	while keep_going:
		
	
		print 'CCW'
		ccw()
		keep_going =False
		keep = True
			
	time.sleep(5)	
	while keep:

		print 'CW'
		cw()
		keep = False
	time.sleep(5)
		
except KeyboardInterrupt:
	print("Ctl C pressed")
	
GPIO.cleanup()
