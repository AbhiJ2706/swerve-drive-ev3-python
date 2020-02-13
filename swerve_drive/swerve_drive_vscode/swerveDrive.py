#!/usr/bin/env python3

'''
Swerve drive: driving based on computer input

Abhi Jain

17 Jun 2019

Receives commands from the computer and sends them to the threads controlling the wheels.
'''

from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, LargeMotor
from time import sleep
import termios, tty, sys
import threading
from threading import Thread
from queue import Queue
from lgMotorThread import lgMotorThread

#allows EV3 to be controlled via keyboard (individually, not simultaneously with other EV3- this is meant for testing)
def keyBoardControl():
    #reads a single character from the keyboard
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
                    m.queue.put("stop")
            elif k == "d":
                for m in motors:
                    m.queue.put("steer")
            elif k == "w":
                for m in motors:
                    m.queue.put("go")
        except Exception as ex:
            print(ex)
            break
        sleep(0.15)

#gets input from computer and sends to motors
def joystickControl():
    #reads a line of inputc
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
            print(j)
            #sending value to each motor
            for m in motors:
                m.queue.put(j)
        except Exception as ex:
            print(ex)
            break

motors = [lgMotorThread(Queue(), LargeMotor(OUTPUT_A), "A", 90),
            lgMotorThread(Queue(), LargeMotor(OUTPUT_B), "B", 90),
            lgMotorThread(Queue(), LargeMotor(OUTPUT_C), "C", 90),
            lgMotorThread(Queue(), LargeMotor(OUTPUT_D), "D", 90)]

for m in motors:
    m.start()

joystickControl()
#keyBoardControl()
