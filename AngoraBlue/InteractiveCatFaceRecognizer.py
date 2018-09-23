#!/usr/bin/env python


import wx

from InteractiveRecognizer import InteractiveRecognizer
import PyInstallerUtils


def main():
    app = wx.App()
    recognizerPath = PyInstallerUtils.resourcePath(
            'recognizers/lbph_cat_faces.xml')
    cascadePath = PyInstallerUtils.resourcePath(
            # Uncomment the next argument for LBP.
            #'cascades/lbpcascade_frontalcatface.xml')
            # Uncomment the next argument for Haar with basic
            # features.
            #'cascades/haarcascade_frontalcatface.xml')
            # Uncomment the next argument for Haar with extended
            # features.
            'cascades/haarcascade_frontalcatface_extended.xml')
    interactiveRecognizer = InteractiveRecognizer(
            recognizerPath, cascadePath,
            scaleFactor=1.2, minNeighbors=1,
            minSizeProportional=(0.125, 0.125),
            title='Interactive Cat Face Recognizer')
    interactiveRecognizer.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
