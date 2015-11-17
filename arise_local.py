#!/usr/bin/env python

# PERSONIFIED SURVEILLANCE CAMERA

# Usage: 
# $ python arise.py <CAMERA_IP>

# Python script by Ross Goodwin and Gene Han
# Made @ ITP (http://itp.nyu.edu), Spring 2015
# For Axis pan-tilt-zoom surveillance camera

# OpenCV (cv2), Numpy, and Requests
# libraries must be installed. The
# rest are in Python standard library.

import cv
import cv2
import urllib 
import numpy as np
from random import choice as rc
from random import randint as ri
import requests
from time import sleep
import subprocess
from sys import argv
from sys import exit
import re
import htmlentitydefs
import time

# word.camera API Endpoint
textEndPt = "https://word.camera/img"

# Function to get zoomed image text from word.camera API
def returnText(img, loc):
    print "SAVING IMAGE"
    x,y,w,h = loc
    roi = img[y:y+h, x:x+w]
    filename = str(int(time.time()))+".jpg"
    cv2.imwrite('img/'+filename, roi)
    payload = {'Script': 'Yes'}
    files = {'file': open('img/'+filename, 'rb')}
    response = requests.post(textEndPt, data=payload, files=files)
    print "TEXT RETRIEVED"
    return [p for p in response.text.split('\n') if p]

# Open Haar Cascade data
face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
profile_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_profileface.xml')
fullbody_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_fullbody.xml')

# Open Motion JPG Stream
# stream = urllib.urlopen('http://'+CAMERA_IP+'/mjpg/video.mjpg')
capture = cv2.VideoCapture(0)

# while 1:
#     _,f = capture.read()
#     cv2.imshow('f',f)

while 1:
    faces = []
    profiles = []
    fullbodies = []

    ret, i = capture.read()

    if ret:

        # Convert to Grayscale
        gray = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)

        # Haar Detection
        faces = face_cascade.detectMultiScale(gray, 1.3, 5) # might need additional args: 1.3, 5
        profiles = profile_cascade.detectMultiScale(gray, 1.3, 5)
        fullbodies = fullbody_cascade.detectMultiScale(gray, 1.3, 5)

        # CODE BELOW WILL DRAW RECTANGLES
        # OVER FACES/PROFILES AND SHOW 
        # MOTION JPG IMAGE STREAM
        # RESULT. UNCOMMENT TO DEBUG 
        # FACE AND PROFILE DETECTION...

        # faces = [(100,100,50,50)]
        # profiles = [(150,150,50,50)]

        for (x,y,w,h) in faces:
            cv2.rectangle(i,(x,y),(x+w,y+h),(255,0,0),2)
        for (x,y,w,h) in profiles:
            cv2.rectangle(i,(x,y),(x+w,y+h),(0,255,0),2)


        # PTZ / DO STUFF WITH FACES
        if len(profiles) + len(faces) + len(fullbodies):

            cv2.imshow('i',i)

            # Image size for zoomVal below
            imgHeight, imgWidth = gray.shape[:2]

            if len(faces) > 0:
                fp = "FACE:"
                x,y,w,h = faces[0]
            elif len(profiles) > 0:
                fp = "PROFILE:"
                x,y,w,h = profiles[0]
            elif len(fullbodies) > 0:
                fp = "BODY:"
                x,y,w,h = fullbodies[0]

            # Print face or profile, location, width/height
            print fp, x, y, w, h

            # Area zoom values
            zoomVal = (imgWidth/w)*ri(10,30) # 100 / zoomVal = portion of screen zoomed
            azVal = "%i,%i,%i"%(x+w/2,y+h/2,zoomVal)

            # Stop panning
            # ptz(continuouspantiltmove="0,0")
            # Go To Device Preset 1
            # ptz(gotodevicepreset="1")
            # Zoom in on face or profile
            # ptz(areazoom=azVal)

            # Send zoomed image to word.camera and read text aloud
            imgTextList = returnText(i,(x,y,w,h))
            # print "TEXT RESULT:"
            # for p in imgTextList:
            #     print p
            imgText = sorted((p for p in imgTextList), key=lambda x: -x.count('#'))[-1]
            print imgText
            proc = subprocess.Popen(["say"], stdin=subprocess.PIPE)
            proc.communicate(imgText)