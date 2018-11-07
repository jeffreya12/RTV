from tkinter import *
from tkinter.ttk import *
import time
import threading

class ServiceLane():
    def __init__(self, identification, capacity, vehicleTypes, imageReference, toldo):
        self.id = identification
        self.vehicleTypes = vehicleTypes
        self.waitingVehicles = []
        self.outsideWaitingVehicles = []
        self.currentVehicle = None
        self.capacity = capacity
        self.pausedTime = 0
        self.image = imageReference

        self.toldo = toldo
        self.toldoId = []
        self.imageId = None
        self.textId = None
        self.newestVehicle = None
        self.remainingAttentionTime = 0

    def addVehicle(self, newVehicle):
        waitingVehiclesLength = len(self.waitingVehicles)
        if waitingVehiclesLength >= self.capacity or (waitingVehiclesLength == self.capacity - 1 and self.currentVehicle != None):
            self.outsideWaitingVehicles.append(newVehicle)
        else:
            self.waitingVehicles.append(newVehicle)

        self.remainingAttentionTime += newVehicle.getAttentionTime()

    def moveOutsideToLane(self):
        if len(self.outsideWaitingVehicles) != 0:
            self.newestVehicle = self.outsideWaitingVehicles.pop(0)
            self.waitingVehicles.append(self.newestVehicle)

    def attendNextVehicle(self):
        if len(self.waitingVehicles) != 0:
            self.currentVehicle = self.waitingVehicles.pop(0)
        else:
            self.currentVehicle = None

    def getLastWaitingVehicle(self):
        if self.capacity == 1:
            return 0
        waiting = len(self.waitingVehicles)
        if waiting >= 2:
            return self.waitingVehicles[-2]
        if waiting < 2:
            return -1
        else:
            return -1

    def updateRemainingTime(self, reduceTime):
        self.remainingAttentionTime = round(self.remainingAttentionTime - reduceTime, 4)
        if self.remainingAttentionTime < 0:
            self.remainingAttentionTime = 0

    def calculateWaitingTimeAndCars(self):
        numberOfCars = 0
        waitingTime = 0
        lastVehicleWaitingTime = 0
        lastVehicleRemainingTime = 0

        if self.currentVehicle != None:
            numberOfCars += 1
            lastVehicleRemainingTime = self.currentVehicle.getRemainingAttentionTime()

        for vehicle in self.waitingVehicles:
            numberOfCars += 1
            lastVehicleWaitingTime += lastVehicleRemainingTime
            waitingTime += lastVehicleWaitingTime
            lastVehicleRemainingTime = vehicle.getRemainingAttentionTime()

        for vehicle in self.outsideWaitingVehicles:
            numberOfCars += 1
            lastVehicleWaitingTime += lastVehicleRemainingTime
            waitingTime += lastVehicleWaitingTime
            lastVehicleRemainingTime = vehicle.getRemainingAttentionTime()

        self.waitingTime = waitingTime
        self.numberOfCars = numberOfCars
        self.lastWaitTime = lastVehicleWaitingTime
        self.lastRemainingTime = lastVehicleRemainingTime


    def getNewestVehicle(self):
        return self.newestVehicle

    def getVehicleTypes(self):
        return self.vehicleTypes

    def getCapacity(self):
        return self.capacity

    def isPaused(self):
        return self.pausedTime > 0

    def setVehicleTypes(self, newVehicleTypes):
        self.vehicleTypes = newVehicleTypes

    def setRemainingTextId(self, textId):
        self.remainingTextId = textId

    def getRaiminingTextId(self):
        return self.remainingTextId

    def setImageId(self, imageId):
        self.imageId = imageId

    def getImageId(self):
        return self.imageId

    def pause(self, pauseTime):
        self.pausedTime = pauseTime

    def getWaitingVehicles(self):
        return self.waitingVehicles

    def getOutsideWaitingVehicles(self):
        return self.outsideWaitingVehicles

    def setPos(self, x, y):
        self.x = x
        self.y = y

class Vehicle():
    def __init__(self, vehicleType, attentionTime, vehicleId):
        self.type = vehicleType
        self.attentionTime = attentionTime
        self.remainingAttentionTime = attentionTime
        self.id = vehicleId
        self.imageId = None
        self.textId = None

    def getId(self):
        return self.id

    def getType(self):
        return self.type

    def getAttentionTime(self):
        return self.attentionTime

    def getRemainingAttentionTime(self):
        return round(self.remainingAttentionTime, 4)

    def reduceRaminingTime(self, reduceTime):
        if self.remainingAttentionTime - reduceTime >= 0:
            self.remainingAttentionTime -= reduceTime

    def getImageId(self):
        return self.imageId

    def getTextId(self):
        return self.textId

    def getAttTimeTextId(self):
        return self.attTimeTextId

    def setImageAndTextId(self, imageId, textId, attentionTimeTextId):
        self.imageId = imageId
        self.textId = textId
        self.attTimeTextId = attentionTimeTextId

	