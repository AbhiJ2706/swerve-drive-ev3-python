'''
Swerve drive: joystick control

Abhi Jain

17 June 2019

Allows the Swerve drive to be controlled by a joystick. The wheels will follow the angle of the joystick (to the nearest 15 degrees) and the speed can be controlled.
'''

import threading, paramiko
from time import sleep
import pygame, math

pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())] #getting joysticks
print(pygame.joystick.get_count())

kill = False #if true, kills the whole program
joystickVals = [0, 0] #x, y values of joystick

'''
This is a modified SSH class from https://daanlenaerts.com/blog/2016/07/01/python-and-ssh-paramiko-shell/
It has added code to stop the entire program if the code on one of the EV3s crashes.
'''
 
class ssh:
    shell = None
    client = None
    transport = None
 
    def __init__(self, address, username, password):
        print("Connecting to server on ip", str(address) + ".")
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)
        self.transport = paramiko.Transport((address, 22))
        self.transport.connect(username=username, password=password)
 
        thread = threading.Thread(target=self.process)
        thread.daemon = True
        thread.start()
 
    def closeConnection(self):
        if(self.client != None):
            self.client.close()
            self.transport.close()
 
    def openShell(self):
        self.shell = self.client.invoke_shell()
 
    def sendShell(self, command):
        if(self.shell):
            self.shell.send(command + '\n')
        else:
            print("Shell not opened.")
 
    def process(self):
        global connection
        while True:
            # Print data when available
            if self.shell != None and self.shell.recv_ready():
                alldata = self.shell.recv(1024)
                while self.shell.recv_ready():
                    alldata += self.shell.recv(1024)
                strdata = str(alldata, "utf8")
                strdata.replace('\r', '')
                print(strdata, end = "")
                #modified part: checks to see if a traceback has been outputted by the EV3
                if strdata.startswith("T"):
                    print(strdata, end = "")
                    global kill
                    kill = True #stops the program
                    print("killed")
                    #while the program is still running it gets all the data being outputted to display the entire traceback
                    while 1:
                        alldata = self.shell.recv(1024)
                        while self.shell.recv_ready():
                            alldata += self.shell.recv(1024)
                        strdata = str(alldata, "utf8")
                        strdata.replace('\r', '')
                        print(strdata, end = "")
                        if(strdata.endswith("$ ")):
                            print("\n$ ", end = "")
            

 
sshUsername = "robot" #username for both robots
sshPassword = "maker" #password
sshServerSteer = "169.254.10.10" #IP for EV3 1 (connected over bluetooth)
sshServerDrive = "192.168.0.112" #IP for EV3 2 (connected over wifi)

#creating SSH for steering EV3
steerConnection = ssh(sshServerSteer, sshUsername, sshPassword) 
steerConnection.openShell()
steerConnection.sendShell("swerve_steer_vscode/swerveSteer.py") #sending command to run the steering code on robot

#creating SSH for driving EV3
driveConnection = ssh(sshServerDrive, sshUsername, sshPassword)
driveConnection.openShell()
driveConnection.sendShell("swerve_drive_vscode/swerveDrive.py") #sending command to run the driving code on robot

angles = [0, 0] #keeping track of joystick angle for continuity
multiplier = 0 #used to modify the angle as needed

i = 0 #there in case of timing the amount of time program runs
sleep(20) #allows the coce on both EV3s to begin running

#rounds angle to nearest 15 degrees (movements finer than this will crash the program on the EV3)
def roundNum(x, base=15):
    rounded = base * round(x/base)
    return rounded

while True:
    joystickVals = [0, 0] #resetting joystick values
    angle = 0 #resetting angle
    #quitting program if keydown event
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            break

    #getting info from joysticks
    for i in range(len(joysticks)): 
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joystickVals[0] = joystick.get_axis(2) #getting joystick x
        joystickVals[1] = joystick.get_axis(3) #getting joystick y
        if joystick.get_button(0): #button for steering
            angle = 1000
        if joystick.get_button(1): #button for steering while driving (doesn't work)
            angle = 2000
            
    if joystickVals[0] != 0 and angle != 1000 and angle != 2000: #avoiding division by 0 and overriding other commands
        angle = int(math.degrees(math.atan2(joystickVals[1], joystickVals[0]))) #calculating angle

        #adjusting angle
        if joystickVals[0] < 0 and joystickVals[1] > 0:
            angle -= 360
        angle += 90
        #checking if joystick is at neutral position
        if joystickVals[1] == -3.0517578125e-05 and joystickVals[0] == -0.007843017578125:
            angle = 0
        #updating angle array
        angles[0] = angle

        #creating continuity
        diff = angles[0] - angles[1] #calculating difference between angles
        if diff < -180: #checking is large jump in angle from - to +
            multiplier += 1
        elif diff > 180: #checking is large jump in angle from + to -
            multiplier -= 1
        angle = angle + 360 * multiplier #modifying angle accordingly
        angles[1] = angles[0] #making current angle previous one
    
    command = "" #command to be sent to steering EV3
    command2 = "" #command to be sent to driving EV3
    
    if angle == 1000 or angle == 2000: 
        command = str(angle)
    else:
        command = str(roundNum(angle))

    #caluclating speed using pythagorean theorem
    spd = joystickVals[0] ** 2 + joystickVals[1] ** 2
    spd = math.sqrt(spd) * 90
    spd = 90 if spd > 90 else spd
    command2 = str(int(spd))
    
    #adding padding to the driving command so it can be read by the EV3
    if len(command2) == 1:
        command2 = "0" + command2
    if angle == 1000: 
        command2 = command2 + "2"
    elif angle == 2000:
        command2 = command2 + "3"
    else:
        command2 = command2 + "1"

    #sending commands to each EV3
    if (i <= 9): 
        print("sending cmd: ", command, command2)
        steerConnection.sendShell(command)
        driveConnection.sendShell(command2)
        pass

    #checking to see if program was killed
    if not kill:
        pass
    else: break
    sleep(0.15)
