#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, MediumMotor
from time import sleep
import termios, tty, sys
import threading
from threading import Thread
from queue import Queue
from medMotorThread import medMotorThread

#gets line of input from computer
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)
    ch = sys.stdin.readline()
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

q = [Queue(), Queue(), Queue(), Queue()]

motors = [medMotorThread(q[0], MediumMotor(OUTPUT_A), [45, 45], 45, "A", args=(0,)),
            medMotorThread(q[1], MediumMotor(OUTPUT_B), [135, 315], 180, "B", args=(0,)),
            medMotorThread(q[2], MediumMotor(OUTPUT_C), [-135, 225], 135, "C", args=(0,)),
            medMotorThread(q[3], MediumMotor(OUTPUT_D), [-45, 135], 180, "D", args=(0,))]

for m in motors:
    m.start()

'''
Outputting to the computer is done as print statements since the SSH on the computer
is built to receive what the EV3 prints.
'''
print(0) #ouputting to computer saying that steering code is ready

while 1:
    try:
        k = getch()
        #getting rid of excess characters
        j = k.strip('\n')
        if j == "0":
            #going into steering mode
            for m in motors:
                m.rotateToState()
                m.saveState()
            sleep(1)
            #telling drive EV3 to spin motors again
            print(4)
            sleep(1.1)
            #going back to forward orientation
            for m in motors:
                m.goToSavedState()
            sleep(1)
            #telling drive EV3 to start looking for objects again
            print(0)
        else:
            print("input not recognized ssh 1:" + "*" + str(j) + "*"+ "\n")
    except Exception as ex:
        print(ex)



