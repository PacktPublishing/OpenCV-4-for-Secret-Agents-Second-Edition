#!/usr/bin/env python


import numpy
import cv2
import os
import threading
import wx

try:
   import cPickle as pickle
except:
   import pickle

import ColorUtils
import GeomUtils
import PyInstallerUtils
import ResizeUtils
import WxUtils


COLOR_Red         = ((  0,   0, 255), 'red')
COLOR_YellowWhite = ((223, 247, 255), 'yellowish white')
COLOR_AmberYellow = ((  0, 191, 255), 'amber or yellow')
COLOR_Green       = ((128, 255, 128), 'green')
COLOR_BlueWhite   = ((255, 231, 223), 'bluish white')
COLOR_BluePurple  = ((255,  64,   0), 'blue or purple')
COLOR_Pink        = ((240, 128, 255), 'pink')

class LivingHeadlights(wx.Frame):

    def __init__(self, configPath, thresholdStep=8.0,
                 minThreshold=191.0, maxThreshold=255.0,
                 minRepeatability=2,
                 minDistBetweenBlobsProportional=0.02,
                 minBlobAreaProportional=0.005,
                 maxBlobAreaProportional=0.1,
                 minBlobCircularity=0.7, cameraDeviceID=0,
                 imageSize=(640, 480),
                 title='The Living Headlights'):

        self.mirrored = True

        self._running = True

        self._configPath = configPath
        self._pixelDistBetweenLights = None
        if os.path.isfile(configPath):
            with open(self._configPath, 'rb') as file:
                self._referencePixelDistBetweenLights = \
                        pickle.load(file)
                self._referenceMetersToCamera = \
                        pickle.load(file)
                self._convertMetersToFeet = pickle.load(file)
        else:
            self._referencePixelDistBetweenLights = None
            self._referenceMetersToCamera = None
            self._convertMetersToFeet = False

        self._capture = cv2.VideoCapture(cameraDeviceID)
        size = ResizeUtils.cvResizeCapture(
                self._capture, imageSize)
        w, h = size
        self._imageWidth, self._imageHeight = w, h

        self._image = None
        self._grayImage = None

        minDistBetweenBlobs = \
                min(w, h) * \
                minDistBetweenBlobsProportional

        area = w * h
        minBlobArea = area * minBlobAreaProportional
        maxBlobArea = area * maxBlobAreaProportional

        detectorParams = cv2.SimpleBlobDetector_Params()

        detectorParams.minDistBetweenBlobs = \
                minDistBetweenBlobs

        detectorParams.thresholdStep = thresholdStep
        detectorParams.minThreshold = minThreshold
        detectorParams.maxThreshold = maxThreshold

        detectorParams.minRepeatability = minRepeatability

        detectorParams.filterByArea = True
        detectorParams.minArea = minBlobArea
        detectorParams.maxArea = maxBlobArea

        detectorParams.filterByColor = True
        detectorParams.blobColor = 255

        detectorParams.filterByCircularity = True
        detectorParams.minCircularity = minBlobCircularity

        detectorParams.filterByInertia = False

        detectorParams.filterByConvexity = False

        self._detector = cv2.SimpleBlobDetector_create(
                detectorParams)

        style = wx.CLOSE_BOX | wx.MINIMIZE_BOX | \
                wx.CAPTION | wx.SYSTEM_MENU | \
                wx.CLIP_CHILDREN
        wx.Frame.__init__(self, None, title=title,
                          style=style, size=size)
        self.SetBackgroundColour(wx.Colour(232, 232, 232))

        self.Bind(wx.EVT_CLOSE, self._onCloseWindow)

        quitCommandID = wx.NewId()
        self.Bind(wx.EVT_MENU, self._onQuitCommand,
                  id=quitCommandID)
        acceleratorTable = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE,
             quitCommandID)
        ])
        self.SetAcceleratorTable(acceleratorTable)

        self._videoPanel = wx.Panel(self, size=size)
        self._videoPanel.Bind(
                wx.EVT_ERASE_BACKGROUND,
                self._onVideoPanelEraseBackground)
        self._videoPanel.Bind(
                wx.EVT_PAINT, self._onVideoPanelPaint)

        self._videoBitmap = None

        self._calibrationTextCtrl = wx.TextCtrl(
                self, style=wx.TE_PROCESS_ENTER)
        self._calibrationTextCtrl.Bind(
                wx.EVT_KEY_UP,
                self._onCalibrationTextCtrlKeyUp)

        self._distanceStaticText = wx.StaticText(self)
        if self._referencePixelDistBetweenLights is None:
            self._showInstructions()
        else:
            self._clearMessage()

        self._calibrationButton = wx.Button(
                self, label='Calibrate')
        self._calibrationButton.Bind(
                wx.EVT_BUTTON, self._calibrate)
        self._calibrationButton.Disable()

        border = 12

        metersButton = wx.RadioButton(self,
                                      label='Meters')
        metersButton.Bind(wx.EVT_RADIOBUTTON,
                          self._onSelectMeters)

        feetButton = wx.RadioButton(self, label='Feet')
        feetButton.Bind(wx.EVT_RADIOBUTTON,
                        self._onSelectFeet)

        if self._convertMetersToFeet:
            feetButton.SetValue(True)
        else:
            metersButton.SetValue(True)

        unitButtonsSizer = wx.BoxSizer(wx.VERTICAL)
        unitButtonsSizer.Add(metersButton)
        unitButtonsSizer.Add(feetButton)

        controlsSizer = wx.BoxSizer(wx.HORIZONTAL)
        style = wx.ALIGN_CENTER_VERTICAL | wx.RIGHT
        controlsSizer.Add(self._calibrationTextCtrl, 0,
                          style, border)
        controlsSizer.Add(unitButtonsSizer, 0, style,
                          border)
        controlsSizer.Add(self._calibrationButton, 0,
                          style, border)
        controlsSizer.Add(self._distanceStaticText, 0,
                          wx.ALIGN_CENTER_VERTICAL)

        rootSizer = wx.BoxSizer(wx.VERTICAL)
        rootSizer.Add(self._videoPanel)
        rootSizer.Add(controlsSizer, 0,
                      wx.EXPAND | wx.ALL, border)
        self.SetSizerAndFit(rootSizer)

        self._captureThread = threading.Thread(
                target=self._runCaptureLoop)
        self._captureThread.start()

    def _onCloseWindow(self, event):
        self._running = False
        self._captureThread.join()
        configDir = os.path.dirname(self._configPath)
        if not os.path.isdir(configDir):
            os.makedirs(configDir)
        with open(self._configPath, 'wb') as file:
            pickle.dump(self._referencePixelDistBetweenLights,
                        file)
            pickle.dump(self._referenceMetersToCamera, file)
            pickle.dump(self._convertMetersToFeet, file)
        self.Destroy()

    def _onQuitCommand(self, event):
        self.Close()

    def _onVideoPanelEraseBackground(self, event):
        pass

    def _onVideoPanelPaint(self, event):

        if self._videoBitmap is None:
            return

        # Show the bitmap.
        dc = wx.BufferedPaintDC(self._videoPanel)
        dc.DrawBitmap(self._videoBitmap, 0, 0)

    def _updateVideoBitmap(self):

        # Convert the image to bitmap format.
        self._videoBitmap = \
            WxUtils.wxBitmapFromCvImage(self._image)

        self._videoPanel.Refresh()

    def _onSelectMeters(self, event):
        self._convertMetersToFeet = False

    def _onSelectFeet(self, event):
        self._convertMetersToFeet = True

    def _onCalibrationTextCtrlKeyUp(self, event):
        self._enableOrDisableCalibrationButton()

    def _calibrate(self, event):
        self._referencePixelDistBetweenLights = \
                self._pixelDistBetweenLights
        s = self._calibrationTextCtrl.GetValue()
        self._calibrationTextCtrl.SetValue('')
        self._referenceMetersToCamera = float(s)
        if self._convertMetersToFeet:
            self._referenceMetersToCamera *= 0.3048

    def _runCaptureLoop(self):
        while self._running:
            success, self._image = self._capture.read(
                    self._image)
            if self._image is not None:
                self._detectAndEstimateDistance()
                if (self.mirrored):
                    self._image[:] = numpy.fliplr(self._image)
                wx.CallAfter(self._updateVideoBitmap)

    def _detectAndEstimateDistance(self):

        self._grayImage = cv2.cvtColor(
                self._image, cv2.COLOR_BGR2GRAY,
                self._grayImage)
        blobs = self._detector.detect(self._grayImage)
        blobsForColors = {}

        for blob in blobs:

            centerXAsInt, centerYAsInt = \
                    (int(n) for n in blob.pt)
            radiusAsInt = int(blob.size)

            minX = max(0, centerXAsInt - radiusAsInt)
            maxX = min(self._imageWidth,
                       centerXAsInt + radiusAsInt)
            minY = max(0, centerYAsInt - radiusAsInt)
            maxY = min(self._imageHeight,
                       centerYAsInt + radiusAsInt)

            region = self._image[minY:maxY, minX:maxX]

            # Get the region's dimensions, which may
            # differ from the blob's diameter if the blob
            # extends past the edge of the image.
            h, w = region.shape[:2]

            meanColor = region.reshape(w * h, 3).mean(0)
            meanHue = ColorUtils.hueFromBGR(meanColor)
            meanSaturation = ColorUtils.saturationFromBGR(
                    meanColor)

            if meanHue < 22.5 or meanHue > 337.5:
                color = COLOR_Red
            elif meanHue < 67.5:
                if meanSaturation < 25.0:
                    color = COLOR_YellowWhite
                else:
                    color = COLOR_AmberYellow
            elif meanHue < 172.5:
                color = COLOR_Green
            elif meanHue < 277.5:
                if meanSaturation < 25.0:
                    color = COLOR_BlueWhite
                else:
                    color = COLOR_BluePurple
            else:
                color = COLOR_Pink

            if color in blobsForColors:
                blobsForColors[color] += [blob]
            else:
                blobsForColors[color] = [blob]

        self._processBlobsForColors(blobsForColors)
        self._enableOrDisableCalibrationButton()

    def _processBlobsForColors(self, blobsForColors):

        self._pixelDistBetweenLights = None

        for color in blobsForColors:

            prevBlob = None

            for blob in blobsForColors[color]:

                colorBGR, colorName = color

                centerAsInts = \
                        tuple(int(n) for n in blob.pt)
                radiusAsInt = int(blob.size)

                # Fill the circle with the selected color.
                cv2.circle(self._image, centerAsInts,
                           radiusAsInt, colorBGR,
                           cv2.FILLED, cv2.LINE_AA)
                # Outline the circle in black.
                cv2.circle(self._image, centerAsInts,
                           radiusAsInt, (0, 0, 0), 1,
                           cv2.LINE_AA)

                if prevBlob is not None:

                    if self._pixelDistBetweenLights is \
                            None:
                        self._pixelDistBetweenLights = \
                                GeomUtils.dist2D(blob.pt,
                                             prevBlob.pt)
                        wx.CallAfter(self._showDistance,
                                     colorName)

                    prevCenterAsInts = \
                        tuple(int(n) for n in prevBlob.pt)

                    # Connect the current and previous
                    # circle with a black line.
                    cv2.line(self._image, prevCenterAsInts,
                             centerAsInts, (0, 0, 0), 1,
                             cv2.LINE_AA)

                prevBlob = blob

    def _enableOrDisableCalibrationButton(self):
        s = self._calibrationTextCtrl.GetValue()
        if len(s) < 1 or \
                self._pixelDistBetweenLights is None:
            self._calibrationButton.Disable()
        else:
            # Validate that the input is a number.
            try:
                float(s)
                self._calibrationButton.Enable()
            except:
                self._calibrationButton.Disable()

    def _showInstructions(self):
        self._showMessage(
                'When a pair of lights is highlighted, '
                'enter the\ndistance and click '
                '"Calibrate".')

    def _showDistance(self, colorName):
        if self._referenceMetersToCamera is None:
            return
        value = self._referenceMetersToCamera * \
                self._referencePixelDistBetweenLights / \
                self._pixelDistBetweenLights
        if self._convertMetersToFeet:
            value /= 0.3048
            unit = 'feet'
        else:
            unit = 'meters'
        self._showMessage(
                'A pair of %s lights was spotted\nat '
                '%.2f %s.' % \
                (colorName, value, unit))

    def _clearMessage(self):
        # Insert an endline for consistent spacing.
        self._showMessage('\n')

    def _showMessage(self, message):
        self._distanceStaticText.SetLabel(message)


def main():
    app = wx.App()
    configPath = PyInstallerUtils.resourcePath(
            'config.dat')
    livingHeadlights = LivingHeadlights(configPath)
    livingHeadlights.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
