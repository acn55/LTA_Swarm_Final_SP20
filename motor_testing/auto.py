import time 
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(17,GPIO.OUT) #left
GPIO.setup(18,GPIO.OUT) #right
GPIO.setup(22,GPIO.OUT) #top
GPIO.setup(23,GPIO.OUT) #bot

#set pwm value
freq1 = freq2 = freq3 = freq4 = 100
dc1 = dc2 = dc3 =dc4 = 0
p=GPIO.PWM(17,freq1)
pwm=GPIO.PWM(18,freq2)
pto=GPIO.PWM(22,freq3)
pbo=GPIO.PWM(23,freq4)
p.start(dc1)
pwm.start(dc2)
pto.start(dc3)
pbo.start(dc4)
#set the initial logic output
def right():
	dc1=0
	p.ChangeDutyCycle(dc1)
	pwm.ChangeDutyCycle(dc2)
def left():
	dc2=0
	p.ChangeDutyCycle(dc1)
	pwm.ChangeDutyCycle(dc2)
def top():
	dc4=0
	pto.ChangeDutyCycle(dc3)
	pbo.ChangeDutyCycle(dc4)
def bot():
	dc3=0
	pto.ChangeDutyCycle(dc3)
	pbo.ChangeDutyCycle(dc4)
def forward():
	p.ChangeDutyCycle(dc1)
	pwm.ChangeDutyCycle(dc2)
	
count = 0 
	
try:
	
	while True:
		print 'time ' + str(count)
		
		if count >= 16:
			count = 0
		
		if count == 0:
			dc1 = dc2 = 50
			forward()
			print 'forward'
		
		elif count == 5:
			dc1 = dc2 = 0 
			forward()
			print 'stop'
		elif count ==6:
			dc2 = 50 
			right()
			print 'right'
			
		elif count == 10:
			dc1 = dc2 = 0 
			forward()
			print 'stop'
			
		elif count == 11:
			dc1 = 50 
			left()
			print 'left'
		
		elif count == 15:
			dc1 = dc2 = 0 
			forward()
			print 'stop'
		time.sleep(1)	
		count += 1	
		
except KeyboardInterrupt:
	print("Ctl C pressed")
	p.stop()
	pwm.stop()
	pto.stop()
	pbo.stop()	
	GPIO.cleanup()
