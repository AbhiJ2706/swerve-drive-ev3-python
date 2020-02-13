#!/usr/bin/env python3

'''
Swerve drive: large motor classs

Abhi Jain

17 June 2019

Controls the speed of a large motor which drives the wheels.
'''

from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, LargeMotor
from time import sleep
import termios, tty, sys
import threading
from threading import Thread
from queue import Queue

class lgMotorThread(threading.Thread):

    def __init__(self, queue, motor, id, rotateSpeed, args=(0,), kwargs=None):
        threading.Thread.__init__(self, args=(0,), kwargs=None)
        self.queue = queue #used to get input from main thread
        self.receive_messages = args[0] #messages received
        self.motor = motor #motor that the thread drives
        self.motor.on_for_degrees(speed=90, degrees=1080)
        self.id = id #id of motor
        self.rotateSpeed = rotateSpeed #speed at which to spin if steering
        self.stateStarted = False #part of a function which doesn't work

    def run(self):
        while 1:
            val = self.queue.get()
            self.runMotor(val)

    def runMotor(self, message="000"):
        spd = int(message[0:2]) #getting speed from command
        typeOfMovement = int(message[2]) #getting type of movement of robot from command
        if not self.stateStarted: #for something that doesn't work
            if typeOfMovement == 0: #turns off motor
                self.motor.off()
            elif typeOfMovement == 1: #moves at specified speed
                self.motor.on(speed=spd)
            elif typeOfMovement == 2: #moves at pre-defined speed
                self.motor.on(speed=self.rotateSpeed)
            elif typeOfMovement == 3: #doesn't work, meant for when robot is rotating and moving at same time
                if not self.stateStarted:
                    self.stateStarted = True
                    def rotate(self):
                        sleep(1)
                        self.motor.on_for_degrees(speed=90, degrees=2160*3)
                        self.stateStarted = False
                    t = Thread(target=rotate, args=(self,))
                    t.start()
            else:
                pass
