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

import cv2 
import urllib 
import numpy as np
from random import choice as rc
from random import randint as ri
import requests
from time import sleep
import subprocess
from sys import argv

# Get camera IP from argv
script, CAMERA_IP = argv

# word.camera API Endpoint
textEndPt = "https://word.camera/img"

# Pan-Tilt-Zoom API Endpoint
controlEndPt = "http://"+CAMERA_IP+"/axis-cgi/com/ptz.cgi"

# Initialize imgBytes variable
imgBytes = ''

# Open Haar Cascade data
face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
profile_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_profileface.xml')

# Function to make Pan-Tilt-Zoom API requests
# (**args will load named arguments as a dictionary)
def ptz(**args):
    return requests.get(controlEndPt, params=args)

# Function to get image text from word.camera API
def returnText(img):
    print "UPLOADING IMAGE"
    payload = {'Script': 'Yes'}
    files = {'file': img}
    response = requests.post(textEndPt, data=payload, files=files)
    print "TEXT RETRIEVED"
    return response.text.split('\n')[0] # 1st paragraph only

# Open Motion JPG Stream
stream = urllib.urlopen('http://'+CAMERA_IP+'/mjpg/video.mjpg')

# Begin by panning right at speed 3
ptz(continuouspantiltmove="3,0")

# Set movingRight boolean to True
movingRight = True

# Loop forever
while 1:

    # Read images from motion jpg stream
    # This code via: 
    # http://stackoverflow.com/questions/21702477/how-to-parse-mjpeg-http-stream-from-ip-camera
    imgBytes+=stream.read(1024)
    a = imgBytes.find('\xff\xd8')
    b = imgBytes.find('\xff\xd9')
    if a!=-1 and b!=-1:
        jpg = imgBytes[a:b+2]
        imgBytes = imgBytes[b+2:]
        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)

        # Convert to Grayscale
        gray = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)

        # Haar Detection
        faces = face_cascade.detectMultiScale(gray, 1.3, 5) # might need additional args: 1.3, 5
        profiles = profile_cascade.detectMultiScale(gray, 1.3, 5)

        # Image size for zoomVal below
        imgHeight, imgWidth = gray.shape[:2]

        # PTZ / DO STUFF WITH FACES
        if len(profiles) > 0 or len(faces) > 0:

            # Prioritize face over profile
            if len(faces) > 0:
                fp = "FACE:"
                x,y,w,h = faces[0]
            elif len(profiles) > 0:
                fp = "PROFILE:"
                x,y,w,h = profiles[0]

            # Print face or profile, location, width/height
            print fp, x, y, w, h

            # Area zoom values
            zoomVal = (imgWidth/w)*ri(30,70) # 100 / zoomVal = portion of screen zoomed
            azVal = "%i,%i,%i"%(x+w/2,y+h/2,zoomVal)

            # Stop panning
            ptz(continuouspantiltmove="0,0")
            # Zoom in on face or profile
            ptz(areazoom=azVal)

            # Send (unzoomed) image to word.camera and read text aloud
            imgText = returnText(i)
            print "TEXT RESULT:"
            print imgText
            proc = subprocess.Popen(["say"], stdin=subprocess.PIPE)
            proc.communicate(imgText)

            # Zoom out and tilt back to horizontal
            ptz(zoom="1", tilt="-180.0")
            sleep(ri(1,4))

            # If previously panning right,
            # begin panning left (or vice versa)
            if movingRight:
                ptz(continuouspantiltmove="-3,0")
                movingRight = False
            else:
                ptz(continuouspantiltmove="3,0")
                movingRight = True

            # Sleep for random interval, 7-15 sec
            sleep(ri(7,15)) 

        # Reset face and profile lists to empty
        faces = []
        profiles = []


        # CODE BELOW WILL DRAW RECTANGLES
        # OVER FACES/PROFILES AND SHOW 
        # MOTION JPG IMAGE STREAM
        # RESULT. UNCOMMENT TO DEBUG 
        # FACE AND PROFILE DETECTION...

        # for (x,y,w,h) in faces:
        #     print "FACE:\t", x, y, w, h
        #     cv2.rectangle(i,(x,y),(x+w,y+h),(255,0,0),2)
        # for (x,y,w,h) in profiles:
        #     print "PROFILE:\t", x, y, w, h
        #     cv2.rectangle(i,(x,y),(x+w,y+h),(0,255,0),2)
        # cv2.imshow('i',i)


        # Exit program on fatal error... (?)
        # (from Stack Overflow code)
        if cv2.waitKey(1) == 27:
            exit(0)