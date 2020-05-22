import time 
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)

GPIO.setup(17,GPIO.OUT) #AIN2
GPIO.setup(18,GPIO.OUT) #AIN1


#set pwm value
freq1= 100
dc1=0
freq2= 100
dc2=0
p=GPIO.PWM(17,freq1)
pwm=GPIO.PWM(18,freq2)

p.start(dc1)
pwm.start(dc2)

#set the initial logic output
def cw():
	dc1=0
	p.ChangeDutyCycle(dc1)
	pwm.ChangeDutyCycle(dc2)
def ccw():
	dc2=0
	p.ChangeDutyCycle(dc1)
	pwm.ChangeDutyCycle(dc2)
buff1 = 0
buff2 = 0
buff3 = 0
keep_going = False
keep = False
try:
	
	while True:
		print dc1,dc2
		command =raw_input("input:")
		if command == 'a':
			keep_going = True
		if command == 'd':
			keep = True	
		if command == 'q':
			dc1 = 0
			dc2 = 0
			buff1 = 0
			buff3 = 0
			buff2 = 0
			cw()
			ccw()
		if command == 'w' and buff3 == 1:
			if buff1 ==1: #increase speed for CCW
				dc1 = dc1 + 10 
				if dc1 >= 90:
					dc1 = 90
				keep_going = True	
			if buff2 ==1: #increase speed for CW
				dc2 = dc2 + 10 
				if dc2 >= 90:
					dc2 = 90
				keep = True	
		if command == 's' and buff3 == 1:
			if buff1 ==1: #decrease speed for CCW
				dc1 = dc1 - 10
				if dc1 <= 5:
					dc1 = 10
				keep_going = True	
			if buff2 ==1: #decrease speed for CW
				dc2 = dc2 - 10 
				if dc2 <= 5:
					dc2 = 10
				keep = True				
		if command == 'z':
			break
	
		while keep_going:
			if buff1 == 0:
				dc1 = 50
				buff3 = 1
			print 'CCW'
			ccw()
			buff1 = 1
			buff2 = 0
			keep_going =False
				
		while keep:
			if buff2 == 0:
				dc2 = 50
				buff3 = 1
			print 'CW'
			cw()
			buff1 = 0
			buff2 = 1
			keep = False
		
except KeyboardInterrupt:
	print("Ctl C pressed")

p.stop()
pwm.stop()	
GPIO.cleanup()
