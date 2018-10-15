#!/usr/bin/env python


import wx

from InteractiveRecognizer import InteractiveRecognizer
import PyInstallerUtils


def main():
    app = wx.App()
    recognizerPath = PyInstallerUtils.resourcePath(
            'recognizers/lbph_human_faces.xml')
    cascadePath = PyInstallerUtils.resourcePath(
            # Uncomment the next argument for LBP.
            #'cascades/lbpcascade_frontalface.xml')
            # Uncomment the next argument for Haar.
            'cascades/haarcascade_frontalface_alt.xml')
    interactiveRecognizer = InteractiveRecognizer(
            recognizerPath, cascadePath,
            title='Interactive Human Face Recognizer')
    interactiveRecognizer.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
