#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 12:54:52 2022

@author: iggy
"""

import numpy as np
import math
from PIL import Image
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


   
#Class which can take images of WB with a ladder and upon calibration hold an 
#an array which allows for determination of infered Mw equivalent at any pixel
class Ladder:
    #Creates numpy array of image upon innitating class as well as one D version
    #of ladder
    def __init__(self, LadderXPixel, LadderImage = r'ladder.tif'):
        self.im = Image.open(LadderImage)
        self.imarray = np.array(self.im)
        self.oneDLadder = [self.imarray[i][LadderXPixel] for i in range(self.imarray.shape[0])]
        #given array of Mw markers and x coordinate of roughly centre of ladder
        #stores y pixel coordinates of Mws of ladder and an array in which 
        #position in the array represents the y co-ordinate and the value the 
        #inferred Mw
    def calibrate(self, MwMarkers, prominance = 1.25):
        self.MwDict = {}
        self.mean = sum(self.oneDLadder)/len(self.oneDLadder)
        for index, y in enumerate(self.oneDLadder):
            if index < 10:
                lowerBound = 0
            else:
                lowerBound = index-10
            if y > prominance*self.mean and y == max(self.oneDLadder[lowerBound:index+10]):
                self.MwDict[MwMarkers.pop(0)] = index
        self.x = []
        self.y = []        
        for i in self.MwDict:
            self.x.append(self.MwDict[i])
            self.y.append(i)
    def fit_curve(self):
        self.param, self.param_cov = curve_fit(self.Mw_function, self.x, self.y)
        self.xprime = np.linspace(1,len(self.oneDLadder), num=len(self.oneDLadder))
        self.curve = (self.param[0]*self.xprime**self.param[1])
        self.inferredValues = [int(self.param[0]*i**self.param[1]) for i in range(1,len(self.oneDLadder))]
    #f(x) = a*x^b to be fit to real data
    def Mw_function(self, x, a, b):
     return a*x**b
    #plots real data pounts and 
    def plot(self, minx = 150):
        plt.plot(self.x, self.y, 'o', color ='red', label ="Real Data")
        plt.plot(self.xprime[minx:], self.curve[minx:], '--', color ='blue', label ="Curve Fit")
        plt.legend()
        plt.show()
    #Residual Standard Error
    def RSE(self):
        y_predicted = np.array([i for index, i in enumerate(self.curve) if index in self.x])
        y_true = np.array(self.y)
        RSS = np.sum(np.square(y_true - y_predicted))
        self.rse = math.sqrt(RSS / (len(y_true) - 2))

    #R2 of curve
    def goodness_of_fit(self):
        self.yInferred = [i for index, i in enumerate(self.curve) if index in self.x]
        self.SSres = sum([(i - self.yInferred[index])**2 for index, i in enumerate(self.y)])
        self.SStot = sum([(i - sum(self.x)/len(self.x))**2 for i in self.x])
        self.Rsquared = 1 - self.SSres/self.SStot
        
            

class ProteinLane:
    #Takes the x coordinates of the lane which you want to analyse
    #the image to analyse and a boolen of whether to average lanes or not
    def __init__(self, LaneXPixel, WBImage = r"OgaRescue800.tif", average = True, twoDInput = True):
        self.average = average
        self.im = Image.open(WBImage)
        self.imarray = np.array(self.im)
        if twoDInput == False:
            self.oneDLanes = np.array([[self.imarray[i][LaneXPixel[index]] for i in range(self.imarray.shape[0])] for index in range(len(LaneXPixel))])
        else:
            self.oneDLanes = [[np.mean(np.array(self.imarray[i][LaneXPixel[index][0]:LaneXPixel[index][1]])) for i in range(self.imarray.shape[0])] for index in range(len(LaneXPixel))]
        if average == True:
            self.oneDLanes = np.mean(self.oneDLanes, axis=0)
        self.total = sum(self.oneDLanes)
    #takes value to divide array of lane, i.e. normalises toa loabing control
    #erases original values
    def normalise(self, loadingControl):
        self.oneDLanes = self.oneDLanes/loadingControl
    #creates a plt object to be graphed takes MwRanges as touple (higher first),
    #pixelCalbration list generated by Ladder.fit_curve and a label
    def plot_profile(self, MwRange, pixelCalibration, avgLabel = "empty"):
        firstPixel = pixelCalibration.index(MwRange[0])
        finalPixel = pixelCalibration.index(MwRange[1])
        if self.average == True:
             plt.plot(pixelCalibration[firstPixel:finalPixel],self.oneDLanes[firstPixel:finalPixel], "-", label = avgLabel)
             plt.legend()
        else:    
            for lane in self.oneDLanes:
                plt.plot(pixelCalibration[firstPixel:finalPixel],lane[firstPixel:finalPixel], "--", label = self.oneDLanes.index(lane))
            plt.legend()
    def intensity_frequency(self, MwRange, pixelCalibration, avgLabel = "Differnce"):
        firstPixel = pixelCalibration.index(MwRange[0])
        finalPixel = pixelCalibration.index(MwRange[1])
        hist, bins = np.histogram(self.oneDLanes[firstPixel:finalPixel])
        print(hist, bins)
        plt.hist(self.oneDLanes[firstPixel:finalPixel], bins = 50, label = avgLabel)
        plt.legend()
        
        
def plot_profile(MwRange, pixelCalibration, oneDLanes, avgLabel = "empty"):
        firstPixel = pixelCalibration.index(MwRange[0])
        finalPixel = pixelCalibration.index(MwRange[1])
        plt.plot(pixelCalibration[firstPixel:finalPixel],oneDLanes[firstPixel:finalPixel], "-", label = avgLabel)
        plt.legend()
