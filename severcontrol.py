import socket
from multiprocessing import Process,Pipe
import time
import control as co
import flightsensor as sensor
import Apriltag 
from Apriltag import Detector
import cv2
serverPort = 12002

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind(('192.168.1.114',serverPort))
serverSocket.listen(1)

running = True          # Looping variable
wp = [0,0,1,0]          # Current waypoint
op_mode = 0             # 0: full auto, 1: waypoint, 2: manual
AT_visible = True      # True: AprilTag currently in view of camera, False: otherwise
AT_ID = 1               # ID of last visible AprilTag
AT_dist = 1           # Last measured distance to AprilTag in meters
AT_ang = 0             # Last measured angle of AprilTag
AT_coords = {1:[0,0],\
             2:[1,3],\
             4:[2,-1],\
             5:[-2,1],\
             3:[1,0],\
             4:[2,0],\
             7:[0,1],\
             6:[-1,-1]}   # Dictionary mapping AprilTag IDs to known (x,y) coordinates
             
# Time of flight distances
# Left, center, right
TOF_dist = [5.8,1.5,0.1]

# Time of flight status
# Left, center, right
# 0: OK
# 1: Danger
# 2: Collision imminent
TOF_status = [0, 1, 2]
#Apriltag section
# visualization = True
at_detector = Detector(searchpath=['apriltags/lib', 'apriltags/lib64'],
                           families='tag36h11',
                           nthreads=1,
                           quad_decimate=1.0,
                           quad_sigma=0.0,
                           refine_edges=1,
                           decode_sharpening=0.25,
                           debug=0)
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_BUFFERSIZE,1)
print("The server is ready to receive")
num=0
try:
    while running:
        connectionSocket, addr = serverSocket.accept()
        message = connectionSocket.recv(1024).decode()
        print("received message: "+message)
        ret, img = cam.read()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if num==5:
            num=0
            tags = at_detector.detect(img)
            if tags:
                AT_ID=int(str(tags[0]))
                print("ID "+ str(tags[0]))
        num=num+1
        # if AT_ang >180 or AT_ang <-180:
            # AT_ang=0
        if message == "quit":
            # Close server (debugging)
            return_msg = "quitting"
            co.quitserver()
            cam.release()
            cv2.destroyAllWindows()
            running = False
        elif message == "forward":
            co.forward()
            # Manual command move forward
            pass
        elif message == "backward":
            co.backward()
            # Manual command move backward
            pass
        elif message == "right":
            #AT_ang=AT_ang+5
            co.right()
            # Manual command pivot right
            pass
        elif message == "left":
            #AT_ang=AT_ang-5
            co.left()
            # Manual command pivot left
            pass
        elif message == "up":
            #AT_dist=AT_dist+0.1
            co.top()
            # Manual command increase altitude
            pass
        elif message == "down":
            #AT_dist=AT_dist-0.1
            co.bot()
            # Manual command decrease altitude
            pass
        elif message == "stop":
            co.stopmotor()
            # Manual command stop motors
            pass
        elif message == "curr wp":
            # Requesting current waypoint
            return_msg = str(wp[0]) + "," + str(wp[1]) + "," + str(wp[2]) + "," + str(wp[3])
        elif message.split(' ')[0] == "mode":
            op_mode = int(message.split(' ')[1])
            print("new op mode: " + str(op_mode))
        elif message.split(' ')[0] == "wp":
            # Waypoint command set new waypoint
            wp[:] = [int(i) for i in message.split(' ')[1].split(',')]
        elif message == "at":
            # Requesting AprilTag data
            return_msg = str(AT_visible)
            if AT_visible and (AT_ID in AT_coords):
                return_msg += "," + str(AT_ID) + "," + str(AT_coords[AT_ID][0]) + "," + str(AT_coords[AT_ID][1]) + "," + str(AT_dist) + "," + str(AT_ang)
        elif message == "tof":
            TOF_dist=sensor.measurement()
            # Requesting time of flight data
            return_msg = ""
            for n in range(3):
                return_msg = return_msg + str(TOF_dist[n]) + ","
            for n in range(3):
                return_msg = return_msg + str(TOF_status[n]) + ","
            return_msg = return_msg[:-1]
        else:
            print("Not recognized")
            return_msg = "Not recognized"
        connectionSocket.send(return_msg.encode())
        connectionSocket.close()
    print ("running = {}".format(running))
    serverSocket.close()
except:
    serverSocket.close()
    raise
