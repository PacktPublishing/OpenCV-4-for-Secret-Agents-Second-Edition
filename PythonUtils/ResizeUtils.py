import numpy # Hint to PyInstaller
from CVForwardCompat import cv2


def cvResizeAspectFill(src, maxSize,
                       upInterpolation=cv2.INTER_LANCZOS4,
                       downInterpolation=cv2.INTER_AREA):
    h, w = src.shape[:2]
    if w > h:
        if w > maxSize:
            interpolation=downInterpolation
        else:
            interpolation=upInterpolation
        h = int(maxSize * h / float(w))
        w = maxSize
    else:
        if h > maxSize:
            interpolation=downInterpolation
        else:
            interpolation=upInterpolation
        w = int(maxSize * w / float(h))
        h = maxSize
    dst = cv2.resize(src, (w, h), interpolation=interpolation)
    return dst

def cvResizeCapture(capture, preferredSize):

    # Try to set the requested dimensions.
    w, h = preferredSize
    capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, w)
    capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, h)

    # Sometimes the dimensions fluctuate at the start of capture.
    # Discard two frames to allow for this.
    capture.read()
    capture.read()

    # Try to return the actual dimensions of the third frame.
    success, image = capture.read()
    if success and image is not None:
        h, w = image.shape[:2]
    return (w, h)
