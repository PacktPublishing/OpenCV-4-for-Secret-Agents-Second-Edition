import numpy
import cv2
import os
import sys
import threading
import wx

import BinasciiUtils
import ResizeUtils
import WxUtils


class InteractiveRecognizer(wx.Frame):

    def __init__(self, recognizerPath, cascadePath,
                 scaleFactor=1.3, minNeighbors=4,
                 minSizeProportional=(0.25, 0.25),
                 rectColor=(0, 255, 0),
                 cameraDeviceID=0, imageSize=(1280, 720),
                 title='Interactive Recognizer'):

        self.mirrored = True

        self._running = True

        self._capture = cv2.VideoCapture(cameraDeviceID)
        size = ResizeUtils.cvResizeCapture(
                self._capture, imageSize)
        self._imageWidth, self._imageHeight = size

        self._image = None
        self._grayImage = None
        self._equalizedGrayImage = None

        self._imageFrontBuffer = None
        self._imageFrontBufferLock = threading.Lock()

        self._currDetectedObject = None

        self._recognizerPath = recognizerPath
        self._recognizer = cv2.face.LBPHFaceRecognizer_create()
        if os.path.isfile(recognizerPath):
            self._recognizer.read(recognizerPath)
            self._recognizerTrained = True
        else:
            self._recognizerTrained = False

        self._detector = cv2.CascadeClassifier(cascadePath)
        self._scaleFactor = scaleFactor
        self._minNeighbors = minNeighbors
        minImageSize = min(self._imageWidth, self._imageHeight)
        self._minSize = (int(minImageSize * minSizeProportional[0]),
                         int(minImageSize * minSizeProportional[1]))
        self._rectColor = rectColor

        style = wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.CAPTION | \
            wx.SYSTEM_MENU | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, None, title=title,
                          style=style, size=size)
        self.SetBackgroundColour(wx.Colour(232, 232, 232))

        self.Bind(wx.EVT_CLOSE, self._onCloseWindow)

        quitCommandID = wx.NewId()
        self.Bind(wx.EVT_MENU, self._onQuitCommand,
                  id=quitCommandID)
        acceleratorTable = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, quitCommandID)
        ])
        self.SetAcceleratorTable(acceleratorTable)

        self._videoPanel = wx.Panel(self, size=size)
        self._videoPanel.Bind(
                wx.EVT_ERASE_BACKGROUND,
                self._onVideoPanelEraseBackground)
        self._videoPanel.Bind(
                wx.EVT_PAINT, self._onVideoPanelPaint)

        self._videoBitmap = None

        self._referenceTextCtrl = wx.TextCtrl(
                self, style=wx.TE_PROCESS_ENTER)
        self._referenceTextCtrl.SetMaxLength(4)
        self._referenceTextCtrl.Bind(
                wx.EVT_KEY_UP, self._onReferenceTextCtrlKeyUp)

        self._predictionStaticText = wx.StaticText(self)
        # Insert an endline for consistent spacing.
        self._predictionStaticText.SetLabel('\n')

        self._updateModelButton = wx.Button(
                self, label='Add to Model')
        self._updateModelButton.Bind(
                wx.EVT_BUTTON, self._updateModel)
        self._updateModelButton.Disable()

        self._clearModelButton = wx.Button(
                self, label='Clear Model')
        self._clearModelButton.Bind(
                wx.EVT_BUTTON, self._clearModel)
        if not self._recognizerTrained:
            self._clearModelButton.Disable()

        border = 12

        controlsSizer = wx.BoxSizer(wx.HORIZONTAL)
        controlsSizer.Add(self._referenceTextCtrl, 0,
                          wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                          border)
        controlsSizer.Add(
                self._updateModelButton, 0,
                wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border)
        controlsSizer.Add(self._predictionStaticText, 0,
                          wx.ALIGN_CENTER_VERTICAL)
        controlsSizer.Add((0, 0), 1) # Spacer
        controlsSizer.Add(self._clearModelButton, 0,
                          wx.ALIGN_CENTER_VERTICAL)

        rootSizer = wx.BoxSizer(wx.VERTICAL)
        rootSizer.Add(self._videoPanel)
        rootSizer.Add(controlsSizer, 0, wx.EXPAND | wx.ALL, border)
        self.SetSizerAndFit(rootSizer)

        self._captureThread = threading.Thread(
                target=self._runCaptureLoop)
        self._captureThread.start()

    def _onCloseWindow(self, event):
        self._running = False
        self._captureThread.join()
        if self._recognizerTrained:
            modelDir = os.path.dirname(self._recognizerPath)
            if not os.path.isdir(modelDir):
                os.makedirs(modelDir)
            self._recognizer.write(self._recognizerPath)
        self.Destroy()

    def _onQuitCommand(self, event):
        self.Close()

    def _onVideoPanelEraseBackground(self, event):
        pass

    def _onVideoPanelPaint(self, event):

        self._imageFrontBufferLock.acquire()

        if self._imageFrontBuffer is None:
            self._imageFrontBufferLock.release()
            return

        # Convert the image to bitmap format.
        self._videoBitmap = \
            WxUtils.wxBitmapFromCvImage(self._imageFrontBuffer)

        self._imageFrontBufferLock.release()

        # Show the bitmap.
        dc = wx.BufferedPaintDC(self._videoPanel)
        dc.DrawBitmap(self._videoBitmap, 0, 0)

    def _onReferenceTextCtrlKeyUp(self, event):
        self._enableOrDisableUpdateModelButton()

    def _updateModel(self, event):
        labelAsStr = self._referenceTextCtrl.GetValue()
        labelAsInt = BinasciiUtils.fourCharsToInt(labelAsStr)
        src = [self._currDetectedObject]
        labels = numpy.array([labelAsInt])
        if self._recognizerTrained:
            self._recognizer.update(src, labels)
        else:
            self._recognizer.train(src, labels)
            self._recognizerTrained = True
            self._clearModelButton.Enable()

    def _clearModel(self, event=None):
        self._recognizerTrained = False
        self._clearModelButton.Disable()
        if os.path.isfile(self._recognizerPath):
            os.remove(self._recognizerPath)
        self._recognizer = cv2.face.LBPHFaceRecognizer_create()

    def _runCaptureLoop(self):
        while self._running:
            success, self._image = self._capture.read(
                    self._image)
            if self._image is not None:
                self._detectAndRecognize()
                if (self.mirrored):
                    self._image[:] = numpy.fliplr(self._image)

                # Perform a thread-safe swap of the front and
                # back image buffers.
                self._imageFrontBufferLock.acquire()
                self._imageFrontBuffer, self._image = \
                    self._image, self._imageFrontBuffer
                self._imageFrontBufferLock.release()

                # Send a refresh event to the video panel so
                # that it will draw the image from the front
                # buffer.
                self._videoPanel.Refresh()

    def _detectAndRecognize(self):
        self._grayImage = cv2.cvtColor(
                self._image, cv2.COLOR_BGR2GRAY,
                self._grayImage)
        self._equalizedGrayImage = cv2.equalizeHist(
                self._grayImage, self._equalizedGrayImage)
        rects = self._detector.detectMultiScale(
                self._equalizedGrayImage,
                scaleFactor=self._scaleFactor,
                minNeighbors=self._minNeighbors,
                minSize=self._minSize)
        for x, y, w, h in rects:
            cv2.rectangle(self._image, (x, y), (x+w, y+h),
                          self._rectColor, 1)
        if len(rects) > 0:
            x, y, w, h = rects[0]
            self._currDetectedObject = cv2.equalizeHist(
                    self._grayImage[y:y+h, x:x+w])
            if self._recognizerTrained:
                try:
                    labelAsInt, distance = self._recognizer.predict(
                            self._currDetectedObject)
                    labelAsStr = BinasciiUtils.intToFourChars(labelAsInt)
                    self._showMessage(
                            'This looks most like %s.\n'
                            'The distance is %.0f.' % \
                            (labelAsStr, distance))
                except cv2.error:
                    print >> sys.stderr, \
                            'Recreating model due to error.'
                    self._clearModel()
            else:
                self._showInstructions()
        else:
            self._currDetectedObject = None
            if self._recognizerTrained:
                self._clearMessage()
            else:
                self._showInstructions()

        self._enableOrDisableUpdateModelButton()

    def _enableOrDisableUpdateModelButton(self):
        labelAsStr = self._referenceTextCtrl.GetValue()
        if len(labelAsStr) < 1 or \
                    self._currDetectedObject is None:
            self._updateModelButton.Disable()
        else:
            self._updateModelButton.Enable()

    def _showInstructions(self):
        self._showMessage(
                'When an object is highlighted, type its name\n'
                '(max 4 chars) and click "Add to Model".')

    def _clearMessage(self):
        # Insert an endline for consistent spacing.
        self._showMessage('\n')

    def _showMessage(self, message):
        wx.CallAfter(self._predictionStaticText.SetLabel, message)
