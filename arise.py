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
import re
import htmlentitydefs
import time

# Get camera IP from argv
script, CAMERA_IP = argv

# word.camera API Endpoint
textEndPt = "https://word.camera/img"

# Pan-Tilt-Zoom API Endpoint
controlEndPt = "http://"+CAMERA_IP+"/axis-cgi/com/ptz.cgi"

# Function to replace xml character references
# NOT NEEDED AT THE MOMENT
#
# def unescape(text):
#     def fixup(m):
#         text = m.group(0)
#         if text[:2] == "&#":
#             # character reference
#             try:
#                 if text[:3] == "&#x":
#                     return unichr(int(text[3:-1], 16))
#                 else:
#                     return unichr(int(text[2:-1]))
#             except ValueError:
#                 pass
#         else:
#             # named entity
#             try:
#                 text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
#             except KeyError:
#                 pass
#         return text # leave as is
#     return re.sub("&#?\w+;", fixup, text)

# Function to make Pan-Tilt-Zoom API requests
# (**args will load named arguments as a dictionary)
def ptz(**args):
    return requests.get(controlEndPt, params=args)

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

# Initialize imgBytes variable
imgBytes = ''

# Open Haar Cascade data
face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
profile_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_profileface.xml')
fullbody_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_fullbody.xml')

# Open Motion JPG Stream
stream = urllib.urlopen('http://'+CAMERA_IP+'/mjpg/video.mjpg')

# Begin by panning right at speed 3
ptz(continuouspantiltmove="3,0")

# Set movingRight boolean to True
movingRight = True

# Loop forever
trigger = 'y'
trigger = raw_input("> ")

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
        fullbodies = fullbody_cascade.detectMultiScale(gray, 1.3, 5)

        # Image size for zoomVal below
        imgHeight, imgWidth = gray.shape[:2]

        # PTZ / DO STUFF WITH FACES
        if trigger == 'x' or len(fullbodies) > 0 or len(profiles) > 0 or len(faces) > 0:
            # Prioritize face over profile
            if trigger == 'x':
                fp = "MANUAL:"
                x = imgWidth/2
                y = imgHeight/2
                w = imgWidth/2
                h = imgHeight/2
            elif len(fullbodies) > 0:
                fp = "BODY:"
                x,y,w,h = fullbodies[0]
            elif len(faces) > 0:
                fp = "FACE:"
                x,y,w,h = faces[0]
            elif len(profiles) > 0:
                fp = "PROFILE:"
                x,y,w,h = profiles[0]

            # Print face or profile, location, width/height
            print fp, x, y, w, h

            # Area zoom values
            zoomVal = (imgWidth/w)*ri(40,70) # 100 / zoomVal = portion of screen zoomed
            azVal = "%i,%i,%i"%(x+w/2,y+h/2,zoomVal)

            # Stop panning
            ptz(continuouspantiltmove="0,0")
            # Zoom in on face or profile
            ptz(areazoom=azVal)

            # Send zoomed image to word.camera and read text aloud
            imgTextList = returnText(i,(x,y,w,h))
            print "TEXT RESULT:"
            for p in imgTextList:
                print p
            imgText = min((p for p in imgTextList), key=lambda x: x.count('#'))
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

            trigger = 'y'
            trigger = raw_input("> ")

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