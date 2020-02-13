#!/usr/bin/env python3

'''
Swerve drive: automatic wall detection: driving portion

Abhi Jain

17 Jun 2019

Gets input from computer and also gets input from the infrared sensor to be controlled.
'''

from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, LargeMotor
from ev3dev2.sensor.lego import InfraredSensor
from time import sleep
import termios, tty, sys
import threading
from threading import Thread
from queue import Queue
from lgMotorThread import lgMotorThread

#reads line from computer
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)
    ch = sys.stdin.readline()
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

ir = InfraredSensor() #infrared sensor

motors = [lgMotorThread(Queue(), LargeMotor(OUTPUT_A), "A", 90),
            lgMotorThread(Queue(), LargeMotor(OUTPUT_B), "B", 90),
            lgMotorThread(Queue(), LargeMotor(OUTPUT_C), "C", 90),
            lgMotorThread(Queue(), LargeMotor(OUTPUT_D), "D", 90)]

#starting motor thread
for m in motors:
    m.start()

while 1:
    try:
        k = getch()
        #getting rid of excess characters
        j = k.strip('\n')
        j = j.strip('\r')
        if j == "0":
            #runs loop which checks for objects
            while 1:
                try:
                    d = ir.proximity * 0.7 #getting distance to object in cm
                    #running motors if distance is large
                    if d > 35:
                        for m in motors:
                            m.queue.put("901")
                    else:
                        '''
                        Outputting to the computer is done as print statements since the SSH on the computer
                        is built to receive what the EV3 prints.
                        '''
                        print(0) #outputting to computer
                        #stopping motors
                        for m in motors:
                            m.queue.put("000")
                        break #stopping loop
                except Exception as ex:
                    print(ex)
                    break
        elif j == "4":
            #putting motors into steering speed (pre-defined)
            for m in motors:
                m.queue.put("002")
        else:
            print("input not recognized ssh 2:" + "*" + str(j) + "*"+ "\n")
            pass
    except Exception as ex:
        print(ex)





