#!/usr/bin/env python


import numpy # Hint to PyInstaller
import cv2
import os
import threading
import wx

from HistogramClassifier import HistogramClassifier
from ImageSearchSession import ImageSearchSession
import PyInstallerUtils
import ResizeUtils
import WxUtils


class Luxocator(wx.Frame):

    def __init__(self, classifierPath, maxImageSize=768,
                 verboseSearchSession=False,
                 verboseClassifier=False):

        style = wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.CAPTION | \
            wx.SYSTEM_MENU | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, None, title='Luxocator', style=style)
        self.SetBackgroundColour(wx.Colour(232, 232, 232))

        self._maxImageSize = maxImageSize
        border = 12
        defaultQuery = 'luxury condo sales'

        self._index = 0
        self._session = ImageSearchSession()
        self._session.verbose = verboseSearchSession
        self._session.search(defaultQuery)

        self._classifier = HistogramClassifier()
        self._classifier.verbose = verboseClassifier
        self._classifier.deserialize(classifierPath)

        self.Bind(wx.EVT_CLOSE, self._onCloseWindow)

        quitCommandID = wx.NewId()
        self.Bind(wx.EVT_MENU, self._onQuitCommand,
                  id=quitCommandID)
        acceleratorTable = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, quitCommandID)
        ])
        self.SetAcceleratorTable(acceleratorTable)

        self._searchCtrl = wx.SearchCtrl(
                self, size=(self._maxImageSize / 3, -1),
                style=wx.TE_PROCESS_ENTER)
        self._searchCtrl.SetValue(defaultQuery)
        self._searchCtrl.Bind(wx.EVT_TEXT_ENTER,
                              self._onSearchEntered)
        self._searchCtrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN,
                              self._onSearchEntered)
        self._searchCtrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN,
                              self._onSearchCanceled)

        self._labelStaticText = wx.StaticText(self)

        self._prevButton = wx.Button(self, label='Prev')
        self._prevButton.Bind(wx.EVT_BUTTON,
                              self._onPrevButtonClicked)

        self._nextButton = wx.Button(self, label='Next')
        self._nextButton.Bind(wx.EVT_BUTTON,
                              self._onNextButtonClicked)

        self._staticBitmap = wx.StaticBitmap(self)

        controlsSizer = wx.BoxSizer(wx.HORIZONTAL)
        controlsSizer.Add(self._searchCtrl, 0,
                          wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                          border)
        controlsSizer.Add((0, 0), 1) # Spacer
        controlsSizer.Add(
                self._labelStaticText, 0, wx.ALIGN_CENTER_VERTICAL)
        controlsSizer.Add((0, 0), 1) # Spacer
        controlsSizer.Add(
                self._prevButton, 0,
                wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT,
                border)
        controlsSizer.Add(
                self._nextButton, 0, wx.ALIGN_CENTER_VERTICAL)

        self._rootSizer = wx.BoxSizer(wx.VERTICAL)
        self._rootSizer.Add(self._staticBitmap, 0,
                            wx.TOP | wx.LEFT | wx.RIGHT, border)
        self._rootSizer.Add(controlsSizer, 0, wx.EXPAND | wx.ALL,
                            border)

        self.SetSizerAndFit(self._rootSizer)

        self._updateImageAndControls()

    @property
    def verboseSearchSession(self):
        return self._session.verbose

    @verboseSearchSession.setter
    def verboseSearchSession(self, value):
        self._session.verbose = value

    @property
    def verboseClassifier(self):
        return self._classifier.verbose

    @verboseClassifier.setter
    def verboseClassifier(self, value):
        self._classifier.verbose = value

    def _onCloseWindow(self, event):
        self.Destroy()

    def _onQuitCommand(self, event):
        self.Close()

    def _onSearchEntered(self, event):
        query = event.GetString()
        if len(query) < 1:
            return
        self._session.search(query)
        self._index = 0
        self._updateImageAndControls()

    def _onSearchCanceled(self, event):
        self._searchCtrl.Clear()

    def _onNextButtonClicked(self, event):
        self._index += 1
        if self._index >= self._session.offset + \
                self._session.numResultsReceived - 1:
            self._session.searchNext()
        self._updateImageAndControls()

    def _onPrevButtonClicked(self, event):
        self._index -= 1
        if self._index < self._session.offset:
            self._session.searchPrev()
        self._updateImageAndControls()

    def _disableControls(self):
        self._searchCtrl.Disable()
        self._prevButton.Disable()
        self._nextButton.Disable()

    def _enableControls(self):
        self._searchCtrl.Enable()
        if self._index > 0:
            self._prevButton.Enable()
        if self._index < self._session.numResultsAvailable - 1:
            self._nextButton.Enable()

    def _updateImageAndControls(self):
        # Disable the controls.
        self._disableControls()
        # Show the busy cursor.
        wx.BeginBusyCursor()
        # Get the image in a background thread.
        threading.Thread(
                target=self._updateImageAndControlsAsync).start()

    def _updateImageAndControlsAsync(self):
        if self._session.numResultsRequested == 0:
            image = None
            label = 'Search had no results'
        else:
            # Get the current image.
            image, url = self._session.getCvImageAndUrl(
                self._index % self._session.numResultsRequested)
            if image is None:
                # Provide an error message.
                label = 'Failed to decode image'
            else:
                # Classify the image.
                label = self._classifier.classify(image, url)
                # Resize the image while maintaining its aspect ratio.
                image = ResizeUtils.cvResizeAspectFill(
                    image, self._maxImageSize)
        # Update the GUI on the main thread.
        wx.CallAfter(self._updateImageAndControlsResync, image,
                     label)

    def _updateImageAndControlsResync(self, image, label):
        # Hide the busy cursor.
        wx.EndBusyCursor()
        if image is None:
            # Provide a black bitmap.
            bitmap = wx.Bitmap(self._maxImageSize,
                               self._maxImageSize / 2)
        else:
            # Convert the image to bitmap format.
            bitmap = WxUtils.wxBitmapFromCvImage(image)
        # Show the bitmap.
        self._staticBitmap.SetBitmap(bitmap)
        # Show the label.
        self._labelStaticText.SetLabel(label)
        # Resize the sizer and frame.
        self._rootSizer.Fit(self)
        # Re-enable the controls.
        self._enableControls()
        # Refresh.
        self.Refresh()

def main():
    os.environ['REQUESTS_CA_BUNDLE'] = \
            PyInstallerUtils.resourcePath('cacert.pem')
    app = wx.App()
    luxocator = Luxocator(
            PyInstallerUtils.resourcePath('classifier.mat'),
            verboseSearchSession=False, verboseClassifier=False)
    luxocator.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()