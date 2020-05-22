import socket
from multiprocessing import Process,Pipe
import time


serverPort = 12002

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind(('192.168.1.114',serverPort))
serverSocket.listen(1)
print("The server is ready to receive")

running = True          # Looping variable
wp = [0,0,1,0]          # Current waypoint
op_mode = 0             # 0: full auto, 1: waypoint, 2: manual
AT_visible = True       # True: AprilTag currently in view of camera, False: otherwise
AT_ID = 3               # ID of last visible AprilTag
AT_dist = 0           # Last measured distance to AprilTag in meters
AT_ang = 0             # Last measured angle of AprilTag
AT_coords = {1:[0,0],\
             3:[1,0],\
             4:[2,0],\
             7:[0,1],\
             13:[-1,-1]}   # Dictionary mapping AprilTag IDs to known (x,y) coordinates
             
# Time of flight distances
# Left, center, right
TOF_dist = [5.8,1.5,0.1]

# Time of flight status
# Left, center, right
# 0: OK
# 1: Danger
# 2: Collision imminent
TOF_status = [0, 1, 2]

try:
    while running:
        connectionSocket, addr = serverSocket.accept()
        message = connectionSocket.recv(1024).decode()
        print("received message: "+message)
        AT_ID=4
        if message == "quit":
            # Close server (debugging)
            return_msg = "quitting"
            running = False
        elif message == "forward":
            # Manual command move forward
            pass
        elif message == "backward":
            # Manual command move backward
            pass
        elif message == "right":
            # Manual command pivot right
            pass
        elif message == "left":
            # Manual command pivot left
            pass
        elif message == "up":
            # Manual command increase altitude
            pass
        elif message == "down":
            # Manual command decrease altitude
            pass
        elif message == "stop":
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
