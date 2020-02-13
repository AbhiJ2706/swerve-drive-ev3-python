#!/usr/bin/env python3

'''
Swerve drive: small motor class

Abhi Jain

17 June 2019

Controls the angle of a small motor which rotates the wheels.
'''

from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, MediumMotor
from time import sleep
import termios, tty, sys
import threading
from threading import Thread
from queue import Queue

#Framework for this class from: https://stackoverflow.com/questions/25904537/how-do-i-send-data-to-a-running-python-thread

class medMotorThread(threading.Thread):

    def __init__(self, queue, motor, state, fullControlState, id, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.queue = queue #gets messages from main thread
        self.receive_messages = args[0] #messages
        self.motor = motor #motor
        self.currentDeg = 0 #current position of motor
        self.prevDeg = 0 #previous position of motor
        self.rotateState = state #angle for steering
        self.fullControlState = fullControlState #for feature that doesn't work
        self.savedState = 0 #saved angle value
        self.id = id #id of motor
        self.rotateStateChosen = False #stops steering angle from being redefined too quickly
        self.inFullState = False #for feature that doesn't work
        self.motor.on_for_degrees(speed=90, degrees=1080)

    def run(self):
        while 1:
            val = self.queue.get()
            self.runMotor(val)

    #rotates to angle that this particular module needs to be in steering mode. Uses a shortest path algorithm to get there.
    def rotateToState(self):
        if self.currentDeg <= 0 and not self.rotateStateChosen:
            post = self.currentDeg % -360
            rotateVal = self.currentDeg
            while rotateVal > post*-360 :
                rotateVal -= 360
                print(rotateVal)
            rotateVal += self.rotateState[0]
            self.queue.put(rotateVal)
            self.rotateStateChosen = True
        elif self.currentDeg > 0 and not self.rotateStateChosen:
            post = self.currentDeg % 360
            rotateVal = self.currentDeg
            while rotateVal < post*360 :
                rotateVal += 360
                print(rotateVal)
            rotateVal += self.rotateState[1]
            self.queue.put(rotateVal)
            self.rotateStateChosen = True

    #gets message and processes it to give angle to wheel
    def runMotor(self, message=0):
        self.currentDeg = message
        rotation = self.currentDeg - self.prevDeg #calculating net rotation
        rotation = rotation * 3 #multiplying by 3 because of gear ratio on real model
        self.motor.on_for_degrees(speed = 90, degrees = rotation)
        self.prevDeg = self.currentDeg

    #saves angle that it was before going to steering mode
    def saveState(self):
        self.savedState = self.prevDeg

    #returns to angle it was before going to steering mode
    def goToSavedState(self):
        self.queue.put(self.savedState)
        self.rotateStateChosen = False

    #for feature that doesn't work
    def rotateToFullControlState(self):
        self.queue.put(self.fullControlState)

