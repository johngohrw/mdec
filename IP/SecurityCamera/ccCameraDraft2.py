'''
timeout is how long it takes for the lights in a motionless area to turn dim.
cv.imshow() and cv.waitKey() will probably cause the program to jam as it tries to load the video. So, if you're facing crashing issues, you can comment them out.
I left them in because I feel that they show crucial information on how it works.
'''
import os
import imutils
import cv2
import argparse as ap
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt

def signalMaxIntensity():
    #TODO: implement the sending action.
    print("Sending signal to set lights to max intensity")

def signalDimIntensity():
    #TODO: implement the sending action.
    print("Sending signal to set lgihts to dim intensity")

def detectMotions(callback):
    #set timeout timer.
    timeout = 100 #arbitrary value.
    timeCounter = 0

    logFile = open("log.txt", 'w')

    #motion detected flag.
    motionDetected = False
    currentDir = os.path.dirname(os.path.realpath(__file__));
    #read video.
    cap = cv2.VideoCapture(os.path.join(currentDir, "basementFootage.mp4"));
    #we dont even use this, but im lazy to refactor.
    firstGFrame = None
    while True:
        ret, currFrame = cap.read()
        print(ret);
        text = "No motion"
        if ret:
            currFrame = imutils.resize(currFrame, width=500)
            currGFrame = cv2.cvtColor(currFrame,cv2.COLOR_BGR2GRAY)
            #apply blurring to smooth the image. - Important preprocessing.
            currGFrame = cv2.GaussianBlur(currGFrame, (21,21), 0)

            #TODO: This code is questionable.. but I'm too lazy to look into it.
            if firstGFrame is None:
                firstGFrame = currGFrame
                avgFrame = currGFrame.copy().astype("float")
                continue
            cv2.accumulateWeighted(currGFrame, avgFrame,0.2)
            frameDelta = cv2.absdiff(cv2.convertScaleAbs(avgFrame), currGFrame)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
            if np.sum(thresh == 255) > 0:
                text = "Motion detected"
                if not motionDetected:
                    #send light signal to turn on.
                    now = datetime.datetime.now()
                    nowStr = str(now.hour) +":" + str(now.minute) + ":"+str(now.second) + " "+ str(now.day) + "/" + str(now.month) + "/" + str(now.year)
                    logFile.write("Set light to maximum intensity at time: " + nowStr +'\n')
                    callback(nowStr)
                motionDetected = True
                #if motion detected, turn lights on. - reset time counter.
                timeCounter = 0

            if motionDetected:
                timeCounter += 1
            if timeCounter >= timeout:
                motionDetected = False
                #send signal to dim lights.
                #turn off counter until lights are turned back on.
                timeCounter = 0

            cv2.putText(currFrame, "Obs: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            cv2.imshow("Frame delta", frameDelta)
            cv2.imshow("Original", currFrame)
            cv2.waitKey(5)
        else:
            break

    logFile.close()
    cap.release()
    cv2.destroyAllWindows()

def hello(string):
    print(string);

if __name__ == '__main__':
    detectMotions(hello);

