import PySpin
import cv2


class PySpinCapture:


    def __init__(self, index, roi, binningRadius=1, isMonochrome=False):

        self._system = PySpin.System.GetInstance()

        self._cameraList = self._system.GetCameras()

        self._camera = self._cameraList.GetByIndex(index)
        self._camera.Init()

        self._nodemap = self._camera.GetNodeMap()

        # Enable continuous acquisition mode.
        nodeAcquisitionMode = PySpin.CEnumerationPtr(self._nodemap.GetNode(
            'AcquisitionMode'))
        nodeAcquisitionModeContinuous = nodeAcquisitionMode.GetEntryByName(
            'Continuous')
        acquisitionModeContinuous = nodeAcquisitionModeContinuous.GetValue()
        nodeAcquisitionMode.SetIntValue(acquisitionModeContinuous)

        # Set the pixel format.
        nodePixelFormat = PySpin.CEnumerationPtr(self._nodemap.GetNode('PixelFormat'))
        if isMonochrome:
            # Enable Mono8 mode.
            nodePixelFormatMono8 = PySpin.CEnumEntryPtr(
                nodePixelFormat.GetEntryByName('Mono8'))
            pixelFormatMono8 = nodePixelFormatMono8.GetValue()
            nodePixelFormat.SetIntValue(pixelFormatMono8)
        else:
            # Enable BGR8 mode.
            nodePixelFormatBGR8 = PySpin.CEnumEntryPtr(
                nodePixelFormat.GetEntryByName('BGR8'))
            pixelFormatBGR8 = nodePixelFormatBGR8.GetValue()
            nodePixelFormat.SetIntValue(pixelFormatBGR8)

        # Set the vertical binning radius.
        # The horizontal binning radius is automatically set to the same value.
        nodeBinningVertical = PySpin.CIntegerPtr(self._nodemap.GetNode(
            'BinningVertical'))
        nodeBinningVertical.SetValue(binningRadius)

        # Set the ROI.
        x, y, w, h  = roi
        nodeOffsetX = PySpin.CIntegerPtr(self._nodemap.GetNode('OffsetX'))
        nodeOffsetX.SetValue(x)
        nodeOffsetY = PySpin.CIntegerPtr(self._nodemap.GetNode('OffsetY'))
        nodeOffsetY.SetValue(y)
        nodeWidth = PySpin.CIntegerPtr(self._nodemap.GetNode('Width'))
        nodeWidth.SetValue(w)
        nodeHeight = PySpin.CIntegerPtr(self._nodemap.GetNode('Height'))
        nodeHeight.SetValue(h)

        self._camera.BeginAcquisition()


    def get(self, propId):
        if propId == cv2.CAP_PROP_FRAME_WIDTH:
            nodeWidth = PySpin.CIntegerPtr(self._nodemap.GetNode('Width'))
            return float(nodeWidth.GetValue())
        if propId == cv2.CAP_PROP_FRAME_HEIGHT:
            nodeHeight = PySpin.CIntegerPtr(self._nodemap.GetNode('Height'))
            return float(nodeHeight.GetValue())
        return 0.0


    def __del__(self):
        self.release()


    def read(self, image=None):

        cameraImage = self._camera.GetNextImage()
        if cameraImage.IsIncomplete():
            return False, None

        h = cameraImage.GetHeight()
        w = cameraImage.GetWidth()
        numChannels = cameraImage.GetNumChannels()
        if numChannels > 1:
            cameraImageData = cameraImage.GetData().reshape(h, w, numChannels)
        else:
            cameraImageData = cameraImage.GetData().reshape(h, w)

        if image is None:
            image = cameraImageData.copy()
        else:
            image[:] = cameraImageData

        cameraImage.Release()

        return True, image


    def release(self):

        self._camera.EndAcquisition()
        self._camera.DeInit()
        del self._camera

        self._cameraList.Clear()

        self._system.ReleaseInstance()
