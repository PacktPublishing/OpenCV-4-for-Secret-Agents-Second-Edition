#!/usr/bin/env python


import numpy # Hint to PyInstaller
import cv2
import getpass
import os
import socket
import sys

import BinasciiUtils
import GeomUtils
import MailUtils
import PyInstallerUtils
import ResizeUtils


def recognizeAndReport(recognizer, grayImage, rects, maxDistance,
                       noun, smtpServer, login, password, fromAddr,
                       toAddrList, ccAddrList):
    for x, y, w, h in rects:
        crop = cv2.equalizeHist(grayImage[y:y+h, x:x+w])
        labelAsInt, distance = recognizer.predict(crop)
        labelAsStr = BinasciiUtils.intToFourChars(labelAsInt)
        print('%s %s %d' % (noun, labelAsStr, distance))
        if distance <= maxDistance:
            subject = 'Angora Blue'
            message = 'We have sighted the %s known as %s.' % \
                    (noun, labelAsStr)
            try:
                problems = MailUtils.sendEmail(
                        fromAddr, toAddrList, ccAddrList, subject,
                        message, login, password, smtpServer)
                if problems:
                    sys.stderr.write(
                            'Email problems: {0}\n'.format(problems))
                else:
                    return True
            except socket.gaierror:
                sys.stderr.write('Unable to reach email server\n')
    return False

def main():

    humanCascadePath = PyInstallerUtils.resourcePath(
            # Uncomment the next argument for LBP.
            #'cascades/lbpcascade_frontalface.xml')
            # Uncomment the next argument for Haar.
            'cascades/haarcascade_frontalface_alt.xml')
    humanRecognizerPath = PyInstallerUtils.resourcePath(
            'recognizers/lbph_human_faces.xml')
    if not os.path.isfile(humanRecognizerPath):
        sys.stderr.write(
                'Human face recognizer not trained. Exiting.\n')
        return

    catCascadePath = PyInstallerUtils.resourcePath(
            # Uncomment the next argument for LBP.
            #'cascades/lbpcascade_frontalcatface.xml')
            # Uncomment the next argument for Haar with basic
            # features.
            #'cascades/haarcascade_frontalcatface.xml')
            # Uncomment the next argument for Haar with extended
            # features.
            'cascades/haarcascade_frontalcatface_extended.xml')
    catRecognizerPath = PyInstallerUtils.resourcePath(
            'recognizers/lbph_cat_faces.xml')
    if not os.path.isfile(catRecognizerPath):
        sys.stderr.write(
                'Cat face recognizer not trained. Exiting.\n')
        return

    print('What email settings shall we use to send alerts?')

    defaultSMTPServer = 'smtp.gmail.com:587'
    print('Enter SMTP server (default: %s):' % defaultSMTPServer)
    smtpServer = sys.stdin.readline().rstrip()
    if not smtpServer:
        smtpServer = defaultSMTPServer

    print('Enter username:')
    login = sys.stdin.readline().rstrip()

    print('Enter password:')
    password = getpass.getpass('')

    defaultAddr = '%s@gmail.com' % login
    print('Enter "from" email address (default: %s):' % defaultAddr)
    fromAddr = sys.stdin.readline().rstrip()
    if not fromAddr:
        fromAddr = defaultAddr

    print('Enter comma-separated "to" email addresses (default: %s):' % defaultAddr)
    toAddrList = sys.stdin.readline().rstrip().split(',')
    if toAddrList == ['']:
        toAddrList = [defaultAddr]

    print('Enter comma-separated "c.c." email addresses:')
    ccAddrList = sys.stdin.readline().rstrip().split(',')

    capture = cv2.VideoCapture(0)
    imageWidth, imageHeight = \
            ResizeUtils.cvResizeCapture(capture, (1280, 720))
    minImageSize = min(imageWidth, imageHeight)

    humanDetector = cv2.CascadeClassifier(humanCascadePath)
    humanRecognizer = cv2.face.LBPHFaceRecognizer_create()
    humanRecognizer.read(humanRecognizerPath)
    humanMinSize = (int(minImageSize * 0.25),
                    int(minImageSize * 0.25))
    humanMaxDistance = 25

    catDetector = cv2.CascadeClassifier(catCascadePath)
    catRecognizer = cv2.face.LBPHFaceRecognizer_create()
    catRecognizer.read(catRecognizerPath)
    catMinSize = (int(minImageSize * 0.125),
                  int(minImageSize * 0.125))
    catMaxDistance = 25

    while True:
        success, image = capture.read()
        if image is not None:
            grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            equalizedGrayImage = cv2.equalizeHist(grayImage)

            humanRects = humanDetector.detectMultiScale(
                    equalizedGrayImage, scaleFactor=1.3,
                    minNeighbors=4, minSize=humanMinSize)
            if recognizeAndReport(
                    humanRecognizer, grayImage, humanRects,
                    humanMaxDistance, 'human', smtpServer, login,
                    password, fromAddr, toAddrList, ccAddrList):
                break

            catRects = catDetector.detectMultiScale(
                    equalizedGrayImage, scaleFactor=1.2,
                    minNeighbors=1, minSize=catMinSize)
            # Reject any cat faces that overlap with human faces.
            catRects = GeomUtils.difference(catRects, humanRects)
            if recognizeAndReport(
                    catRecognizer, grayImage, catRects,
                    catMaxDistance, 'cat', smtpServer, login,
                    password, fromAddr, toAddrList, ccAddrList):
                break

if __name__ == '__main__':
    main()
