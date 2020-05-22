import time
import VL53L0X
import RPi.GPIO as GPIO

XSHUT=[15,16,18]
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
# Setup GPIO for shutdown pins on each VL53L0X
for pin in XSHUT:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Keep all low for 500 ms or so to make sure they reset
time.sleep(0.5)

# Create one object per VL53L0X passing the address to give to
# each.
tof_objects = {}
tof_objects[XSHUT[0]] = VL53L0X.VL53L0X(address=0x2A)
tof_objects[XSHUT[1]] = VL53L0X.VL53L0X(address=0x2C)
tof_objects[XSHUT[2]] = VL53L0X.VL53L0X(address=0x2E)

# Set shutdown pin high for VL53L0X then call to start ranging
for pin in XSHUT:
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.50)
    tof_objects[pin].start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)


def measurement():
        global distances 

        distance1=tof_objects[XSHUT[0]].get_distance()
        distance2=tof_objects[XSHUT[1]].get_distance()
        distance3=tof_objects[XSHUT[2]].get_distance()
        distances=[distance1,distance2,distance3]
        
        return distances

if __name__ == '__main__': 
    con=True
    try:
        while(con):
            a=measurement()
            print(a)

            time.sleep(0.1)
    except KeyboardInterrupt:
        con=False
        print("Ctl C pressed")
        tof_objects[XSHUT[0]].stop_ranging()
        tof_objects[XSHUT[1]].stop_ranging()
        tof_objects[XSHUT[2]].stop_ranging()
        GPIO.cleanup()


