#!/usr/bin/env python3

'''
Swerve drive: steering based on input

Abhi Jain

17 June 2019

Gets input and sends it to the steering motors to steer the model
'''

from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, MediumMotor
from time import sleep
import termios, tty, sys
import threading
from threading import Thread
from queue import Queue
from medMotorThread import medMotorThread

#allows EV3 to be controlled via keyboard (individually, not simultaneously with other EV3- this is meant for testing)
def keyBoardControl():
    #reads a single character from the computer
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    while 1:
        try:
            k = getch()
            j = k.strip('\n')
            if k == "a":
                for m in motors:
                    m.queue.put(m.currentDeg + 360)
            elif k == "d":
                for m in motors:
                    m.queue.put(m.currentDeg - 360)
            elif k == "w":
                for m in motors:
                    m.rotateToState()
                    m.saveState()
            elif k == "s":
                for m in motors:
                    m.goToSavedState()
            elif k == "e":
                for m in motors:
                    m.queue.put(0)
            elif k == "q":
                for m in motors:
                    m.queue.put(0)
                break
            elif k == "f":
                for m in motors:
                    m.rotateToFullControlState()
                    m.saveState()
                for m in motors:
                    m.goFullControl()

        except Exception as ex:
            print(ex)
            break
        sleep(0.15)

#gets input from joystick
def joystickControl():
    #reads full line of input
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)
        ch = sys.stdin.readline()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    while 1:
        try:
            k = getch()
            j = k.strip('\n')
            currentDeg = int(j)
            #putting motors into steering state
            if currentDeg == 1000:
                for m in motors:
                    m.rotateToState()
                    m.saveState()
            #doesn't work (was supposed to steer and drive robot at same time)
            elif currentDeg == 2000:
                for m in motors:
                    m.rotateToFullControlState()
                    m.saveState()
                sleep(1)
                for m in motors:
                    m.motor.on_for_degrees(speed=45, degrees=1080)
                for m in motors:
                    m.goToSavedState()
            #used for following angle of joystick
            else:
                for m in motors:
                    m.queue.put(currentDeg)
                    m.rotateStateChosen = False
        except Exception as ex:
            print(ex)
            break
        sleep(0.15)

q = [Queue(), Queue(), Queue(), Queue()]

motors = [medMotorThread(q[0], MediumMotor(OUTPUT_A), [45, 45], 180, "A", args=(0,)),
            medMotorThread(q[1], MediumMotor(OUTPUT_B), [135, 135], 0, "B", args=(0,)),
            medMotorThread(q[2], MediumMotor(OUTPUT_C), [-135, -135], 45, "C", args=(0,)),
            medMotorThread(q[3], MediumMotor(OUTPUT_D), [-45, -45], 90, "D-", args=(0,))]

for m in motors:
    m.start()

print("input")

#keyBoardControl()
joystickControl()

print("exiting")
exit()
