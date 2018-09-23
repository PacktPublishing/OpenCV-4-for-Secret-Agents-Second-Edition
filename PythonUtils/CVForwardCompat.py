import numpy # Hint to PyInstaller
import cv2

CV_MAJOR_VERSION, CV_MINOR_VERSION, CV_SUBMINOR_VERSION = \
        (int(s.split('-')[0]) for s in cv2.__version__.split('.'))
if CV_MAJOR_VERSION > 2:

    # Create a dummy object in lieu of the cv2.cv module.
    cv2.cv = lambda: None

    # Create aliases to make parts of the OpenCV 3.x library
    # backward-compatible.

    cv2.CV_AA = cv2.LINE_AA
    cv2.CV_LOAD_IMAGE_COLOR = cv2.IMREAD_COLOR
    cv2.SimpleBlobDetector = cv2.SimpleBlobDetector_create
    cv2.cv.CV_CAP_PROP_FRAME_WIDTH = cv2.CAP_PROP_FRAME_WIDTH
    cv2.cv.CV_CAP_PROP_FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT
    cv2.cv.CV_FILLED = cv2.FILLED
    cv2.cv.CV_HAAR_SCALE_IMAGE = cv2.CASCADE_SCALE_IMAGE

    try:
        class LBPHFaceRecognizer:

            def __init__(self):
                if CV_MAJOR_VERSION < 4:
                    self._recognizer = cv2.face.createLBPHFaceRecognizer()
                else:
                    self._recognizer = cv2.face.LBPHFaceRecognizer_create()

            def train(self, src, labels):
                self._recognizer.train(src, labels)

            def update(self, src, labels):
                self._recognizer.update(src, labels)

            def predict(self, src):
                if CV_MAJOR_VERSION == 3 and CV_MINOR_VERSION < 2:
                    result = cv2.face.MinDistancePredictCollector_create()
                    self._recognizer.predict(src, result)
                    return result.getLabel(), result.getDist()
                else:
                    return self._recognizer.predict(src)

            def save(self, filename):
                if CV_MAJOR_VERSION < 4:
                    self._recognizer.save(filename)
                else:
                    self._recognizer.write(filename)

            def load(self, filename):
                if CV_MAJOR_VERSION < 4:
                    self._recognizer.load(filename)
                else:
                    self._recognizer.read(filename)

        cv2.createLBPHFaceRecognizer = lambda: LBPHFaceRecognizer()

    except AttributeError:
        # The face module from opencv_contrib is unavailable.
        pass
