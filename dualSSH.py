'''
Swerve drive: automatic obstacle detection

Abhi Jain

17 June 2019

This is the "middle man". It allows the 2 EV3s to send each other command in the form of integers, so that the timing of
detecting the wall, stopping, changing wheel position, steering, and the rechanging position can be achieved.

Note that this class is generic and can, in theory, be used to facilitate messaging between any 2 devices connected over SSH as well as any 2-EV3 auto mode.
'''


import threading, paramiko
from time import sleep

kill = False #will kill the program if changed

'''
This is a modified SSH class from https://daanlenaerts.com/blog/2016/07/01/python-and-ssh-paramiko-shell/
It has added code to stop the entire program if the code on one of the EV3s crashes, and to establish communication between 2 EV3s
'''

class dualSSH:
    shell_device1 = None #shell for device 1
    shell_device2 = None #shell for device 2
    client_device1 = None #client for device 1
    client_device2 = None #client for device 2
    transport1 = None #transport for device 1
    transport2 = None #transport for device 2
 
    def __init__(self, address1, address2, username, password):
        print("Connecting to server on ip", str(address1) + ".")
        print("Connecting to server on ip", str(address2) + ".")

        #creating shell for device 1
        self.client_device1 = paramiko.client.SSHClient()
        self.client_device1.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client_device1.connect(address1, username=username, password=password, look_for_keys=False)
        self.transport1 = paramiko.Transport((address1, 22))
        self.transport1.connect(username=username, password=password)

        #creating shell for device 2
        self.client_device2 = paramiko.client.SSHClient()
        self.client_device2.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client_device2.connect(address2, username=username, password=password, look_for_keys=False)
        self.transport2 = paramiko.Transport((address2, 22))
        self.transport2.connect(username=username, password=password)

        #thread for getting and processing input for device 1
        thread1 = threading.Thread(target=self.processThread1)
        thread1.daemon = True
        thread1.start()

        #thread for getting and processing input for device 2
        thread2 = threading.Thread(target=self.processThread2)
        thread2.daemon = True
        thread2.start()
    
    #closes connection
    def closeConnection(self):
        if(self.client_device1 != None and self.client_device2 != None):
            self.client_device1.close()
            self.client_device2.close()
            self.transport1.close()
            self.transport2.close()

    #opens connection 
    def openShell(self):
        self.shell_device1 = self.client_device1.invoke_shell()
        self.shell_device2 = self.client_device2.invoke_shell()

    #sends instructions to device 1
    def sendShellDevice1(self, command):
        if(self.shell_device1):
            self.shell_device1.send(command + '\n')
        else:
            print("Shell not opened.")

    #sends instructions to device 1
    def sendShellDevice2(self, command):
        if(self.shell_device2):
            self.shell_device2.send(command + '\n')
        else:
            print("Shell not opened.")

    #gets and processes input for device 1
    def processThread1(self):
        sleep(20)
        global connection, kill
        while True:
            # Print data when available
            if self.shell_device1 != None and self.shell_device1.recv_ready():
                alldata = self.shell_device1.recv(1024)
                while self.shell_device1.recv_ready():
                    alldata += self.shell_device1.recv(1024)
                    print("in here")
                strdata = str(alldata, "utf8")
                strdata = strdata.strip('\r')
                print("data received ssh 1 is: " + "*" + strdata + "*", end = "")
                #checking if a traceback has been sent
                if strdata.startswith("T"):
                    print(strdata, end = "")
                    kill = True #killing program
                    #gets and prints data from EV3 for as long as possible to display whole traceback
                    while 1:
                        alldata = self.shell_device1.recv(1024)
                        while self.shell_device1.recv_ready():
                            alldata += self.shell_device1.recv(1024)
                        strdata = str(alldata, "utf8")
                        strdata = strdata.strip('\r')
                        print(strdata, end = "")
                        if(strdata.endswith("$ ")):
                            print("\n$ ", end = "")
                else:
                    #testing the input to see if it can become a usable command for the robot
                    try:
                        #getting rid of excess characters
                        strdata = strdata.strip('\n')
                        strdata = strdata.strip('\r')
                        strdata = strdata.strip(' ')
                        #making sure string is not empty
                        if len(strdata) != 0:
                            a = int(strdata) #turning into int (if not possible, except block runs and command is not sent)
                            print("sending to ssh 2: *", a , "*") 
                            self.sendShellDevice2(strdata) #sending command to other device
                        else:
                            print("empty string")
                    except Exception as ex:
                        print("-------------------------------------------------------------------------------")
                        print(ex)
                        print("-------------------------------------------------------------------------------")
            else:
                #print("shell not ready")
                pass

    #gets and processes input for device 2
    def processThread2(self):
        sleep(20)
        global connection, kill
        while True:
            if self.shell_device2 != None and self.shell_device2.recv_ready():
                alldata = self.shell_device2.recv(1024)
                while self.shell_device2.recv_ready():
                    alldata += self.shell_device2.recv(1024)
                    print("in here")
                strdata = str(alldata, "utf8")
                strdata = strdata.strip('\r')
                print("data received ssh 2 is: " + "*" + strdata + "*", end = "")
                #checking if a traceback has been sent
                if strdata.startswith("T"):
                    kill = True #killing program
                    print(strdata, end = "")
                    #gets and prints data from EV3 for as long as possible to display whole traceback
                    while 1:
                        alldata = self.shell_device2.recv(1024)
                        while self.shell_device2.recv_ready():
                            alldata += self.shell_device1.recv(1024)
                        strdata = str(alldata, "utf8")
                        strdata = strdata.strip('\r')
                        print(strdata, end = "")
                        if(strdata.endswith("$ ")):
                            print("\n$ ", end = "")
                else:
                    #testing the input to see if it can become a usable command for the robot
                    try:
                        #getting rid of excess characters
                        strdata = strdata.strip('\n')
                        strdata = strdata.strip('\r')
                        strdata = strdata.strip(' ')
                        #making sure string is not empty
                        if len(strdata) != 0:
                            a = int(strdata) #turning into int (if not possible, except block runs and command is not sent)
                            print("sending to ssh 1: *", a , "*") 
                            self.sendShellDevice1(strdata) #sending command to other device
                        else:
                            print("empty string")
                    except Exception as ex:
                        print("-------------------------------------------------------------------------------")
                        print(ex)
                        print("-------------------------------------------------------------------------------")
            else:
                #print("shell not ready")
                pass
                        



autoConnection = dualSSH("169.254.10.10", "192.168.0.112", "robot", "maker") #creating connection
autoConnection.openShell() #opening shell
autoConnection.sendShellDevice1("swerve_steer_vscode/swerveSteerAuto.py") #sending command to run code on steering EV3
autoConnection.sendShellDevice2("swerve_drive_vscode/swerveAutoDrive.py") #sending command to run code on driving EV3
while not kill: #keeping the program alive (so threads can be daemon)
    print("running!"+ "\n")
    sleep(1)
    pass
                
