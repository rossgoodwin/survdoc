import cv2
import urllib 
import numpy as np
from random import choice as rc
from random import randint as ri
import requests
from time import sleep

CAMERA_IP = "10.0.0.3"

stream=urllib.urlopen('http://'+CAMERA_IP+'/mjpg/video.mjpg')
controlEndPt = "http://"+CAMERA_IP+"/axis-cgi/com/ptz.cgi"
imgBytes=''
face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
profile_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_profileface.xml')
# eye_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_eye.xml')

# This code via: 
# http://stackoverflow.com/questions/21702477/how-to-parse-mjpeg-http-stream-from-ip-camera

def ptz(**args):
    requests.get(controlEndPt, params=args)

ptz(continuouspantiltmove="3,0")

movingRight = True
# currentFace = False

while 1:

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

        # image size
        imgHeight, imgWidth = gray.shape[:2]

        # PTZ / DO STUFF WITH FACES
        if len(profiles) > 0 or len(faces) > 0:
            # currentFace = True
            if len(profiles) > 0:
                fp = "PROFILE:\t"
                x,y,w,h = profiles[0]
            elif len(faces) > 0:
                fp = "FACE:\t"
                x,y,w,h = faces[0]

            print fp, x, y, w, h

            # if w > 99 and h > 99:
            azVal = "%i,%i,%i"%(x+w/2,y+h/2,(imgWidth/w)*50)
            ptz(continuouspantiltmove="0,0", areazoom=azVal)
            # leftRight = rc(["-1", "1"])
            # upDown = rc(["-1", "1"])
            # ptz(continuouspantiltmove=leftRight+","+upDown)
            sleep(10)
            ptz(zoom="1", tilt="-180.0")
            sleep(1)
            if movingRight:
                ptz(continuouspantiltmove="-3,0")
                movingRight = False
            else:
                ptz(continuouspantiltmove="3,0")
                movingRight = True
            sleep(10)
            # currentFace = False

        faces = []
        profiles = []
            # ptz(continuouspantiltmove=0,0)

        # Draw Rectangles
        # for (x,y,w,h) in faces:
        #     print "FACE:\t", x, y, w, h
        #     cv2.rectangle(i,(x,y),(x+w,y+h),(255,0,0),2)

        # for (x,y,w,h) in profiles:
        #     print "PROFILE:\t", x, y, w, h
        #     cv2.rectangle(i,(x,y),(x+w,y+h),(0,255,0),2)

        # Show Image
        # cv2.imshow('i',i)

        # Not sure what this is...
        if cv2.waitKey(1) == 27:
            exit(0)