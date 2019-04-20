#!/usr/bin/env python


import collections
import threading
import timeit

import numpy
import cv2
import wx

import pyfftw.interfaces.cache
from pyfftw.interfaces.scipy_fftpack import fft
from pyfftw.interfaces.scipy_fftpack import ifft
from scipy.fftpack import fftfreq

import WxUtils

try:
    import PySpinCapture
except ImportError:
    PySpinCapture = None


class Sunbaker(wx.Frame):

    def __init__(self, capture, isCaptureMonochrome=False,
                 maxHistoryLength=360,
                 minHz=5.0/6.0, maxHz=1.0,
                 amplification=32.0, numPyramidLevels=2,
                 useLaplacianPyramid=True,
                 useGrayOverlay=True,
                 numFFTThreads=4, numIFFTThreads=4,
                 title='Sunbaker'):

        self.mirrored = True

        self._running = True

        self._capture = capture

        # Sometimes the dimensions fluctuate at the start of
        # capture.
        # Discard two frames to allow for this.
        capture.read()
        capture.read()

        success, image = capture.read()
        if success:
            # Use the actual image dimensions.
            h, w = image.shape[:2]
            isCaptureMonochrome = (len(image.shape) == 2)
        else:
            # Use the nominal image dimensions.
            w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        size = (w, h)
        if isCaptureMonochrome:
            useGrayOverlay = True
        self._isCaptureMonochrome = isCaptureMonochrome

        self._image = None

        self._imageFrontBuffer = None
        self._imageFrontBufferLock = threading.Lock()

        self._useGrayOverlay = useGrayOverlay
        if useGrayOverlay:
            historyShape = (maxHistoryLength,
                            h >> numPyramidLevels,
                            w >> numPyramidLevels)
        else:
            historyShape = (maxHistoryLength,
                            h >> numPyramidLevels,
                            w >> numPyramidLevels, 3)

        self._maxHistoryLength = maxHistoryLength
        self._history = numpy.empty(historyShape,
                                    numpy.float32)
        self._historyTimestamps = collections.deque()

        self._numPyramidLevels = numPyramidLevels
        self._useLaplacianPyramid = useLaplacianPyramid

        self._minHz = minHz
        self._maxHz = maxHz
        self._amplification = amplification

        self._numFFTThreads = numFFTThreads
        self._numIFFTThreads = numIFFTThreads

        pyfftw.interfaces.cache.enable()
        pyfftw.interfaces.cache.set_keepalive_time(1.0)

        style = wx.CLOSE_BOX | wx.MINIMIZE_BOX | \
                wx.CAPTION | wx.SYSTEM_MENU | \
                wx.CLIP_CHILDREN
        wx.Frame.__init__(self, None, title=title,
                          style=style, size=size)

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

        self._fpsStaticText = wx.StaticText(self)

        border = 12

        controlsSizer = wx.BoxSizer(wx.HORIZONTAL)
        controlsSizer.Add(self._fpsStaticText, 0,
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
        pyfftw.interfaces.cache.disable()
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

    def _runCaptureLoop(self):

        while self._running:
            success, self._image = self._capture.read(
                    self._image)
            if self._image is not None:
                self._applyEulerianVideoMagnification()
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

    def _applyEulerianVideoMagnification(self):

        timestamp = timeit.default_timer()

        if self._useGrayOverlay and \
               not self._isCaptureMonochrome:
            smallImage = cv2.cvtColor(
                    self._image, cv2.COLOR_BGR2GRAY).astype(
                            numpy.float32)
        else:
            smallImage = self._image.astype(numpy.float32)

        # Downsample the image using a pyramid technique.
        i = 0
        while i < self._numPyramidLevels:
            smallImage = cv2.pyrDown(smallImage)
            i += 1
        if self._useLaplacianPyramid:
            smallImage[:] -= \
                cv2.pyrUp(cv2.pyrDown(smallImage))

        historyLength = len(self._historyTimestamps)

        if historyLength < self._maxHistoryLength - 1:

            # Append the new image and timestamp to the
            # history.
            self._history[historyLength] = smallImage
            self._historyTimestamps.append(timestamp)

            # The history is still not full, so wait.
            return

        if historyLength == self._maxHistoryLength - 1:
            # Append the new image and timestamp to the
            # history.
            self._history[historyLength] = smallImage
            self._historyTimestamps.append(timestamp)
        else:
            # Drop the oldest image and timestamp from the
            # history and append the new ones.
            self._history[:-1] = self._history[1:]
            self._historyTimestamps.popleft()
            self._history[-1] = smallImage
            self._historyTimestamps.append(timestamp)

        # The history is full, so process it.

        # Find the average length of time per frame.
        startTime = self._historyTimestamps[0]
        endTime = self._historyTimestamps[-1]
        timeElapsed = endTime - startTime
        timePerFrame = \
                timeElapsed / self._maxHistoryLength
        fps = 1.0 / timePerFrame
        wx.CallAfter(self._fpsStaticText.SetLabel,
                     'FPS:  %.1f' % fps)

        # Apply the temporal bandpass filter.
        fftResult = fft(self._history, axis=0,
                        threads=self._numFFTThreads)
        frequencies = fftfreq(
                self._maxHistoryLength, d=timePerFrame)
        lowBound = (numpy.abs(
                frequencies - self._minHz)).argmin()
        highBound = (numpy.abs(
                frequencies - self._maxHz)).argmin()
        fftResult[:lowBound] = 0j
        fftResult[highBound:-highBound] = 0j
        fftResult[-lowBound:] = 0j
        ifftResult = ifft(fftResult, axis=0,
                          threads=self._numIFFTThreads)

        # Amplify the result and overlay it on the
        # original image.
        overlay = numpy.real(ifftResult[-1]) * \
                          self._amplification
        i = 0
        while i < self._numPyramidLevels:
            overlay = cv2.pyrUp(overlay)
            i += 1
        if self._useGrayOverlay and \
                not self._isCaptureMonochrome:
            overlay = cv2.cvtColor(overlay,
                                   cv2.COLOR_GRAY2BGR)
        cv2.add(self._image, overlay, self._image,
                dtype=cv2.CV_8U)


def main():

    app = wx.App()

    if PySpinCapture is not None and \
            PySpinCapture.getNumCameras() > 0:
        isCaptureMonochrome = True
        capture = PySpinCapture.PySpinCapture(
                0, roi=(0, 0, 960, 600), binningRadius=2,
                isMonochrome=isCaptureMonochrome)
    else:
        isCaptureMonochrome = False
        capture = cv2.VideoCapture(0)

        # 320x240 @ 187 FPS
        #capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        #capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        #capture.set(cv2.CAP_PROP_FPS, 187)

        # 640x480 @ 60 FPS
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        capture.set(cv2.CAP_PROP_FPS, 60)

    # Show motion at edges with grayscale contrast.
    sunbaker = Sunbaker(capture, isCaptureMonochrome)

    sunbaker.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
