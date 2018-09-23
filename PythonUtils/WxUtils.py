import numpy # Hint to PyInstaller
from CVForwardCompat import cv2
import wx


# Try to determine whether we are on Raspberry Pi.
IS_RASPBERRY_PI = False
try:
    with open('/proc/cpuinfo') as f:
        for line in f:
            line = line.strip()
            if line.startswith('Hardware') and \
                    line.endswith('BCM2708'):
                IS_RASPBERRY_PI = True
                break
except:
    pass

if IS_RASPBERRY_PI:
    def wxBitmapFromCvImage(image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image.shape[:2]
        wxImage = wx.ImageFromBuffer(w, h, image)
        bitmap = wx.BitmapFromImage(wxImage)
        return bitmap
else:
    def wxBitmapFromCvImage(image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image.shape[:2]
        # The following conversion fails on Raspberry Pi.
        bitmap = wx.BitmapFromBuffer(w, h, image)
        return bitmap
