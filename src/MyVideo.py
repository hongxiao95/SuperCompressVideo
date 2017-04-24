import cv2
from PIL import Image
import numpy

class MyVideo(object):
    """MyVideo 类，封装过的openCv读取到的视频及一些常用操作
    """

    def __init__(self, sourceVideoFileName, smallRectWidthInPix):
        self.sourceVideoFileName = sourceVideoFileName
        self.cap = cv2.VideoCapture(self.sourceVideoFileName)
        self.initVideoInfo()
        self.smallRectWidthInPix = min(smallRectWidthInPix, self.frameHeight, self.frameWidth)
        self.initRectsInfo()
    
    def initVideoInfo(self):
        """读取视频基本信息
        """
        self.frameWidth = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frameCount = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = float(self.cap.get(cv2.CAP_PROP_FPS))
    
    def initRectsInfo(self):
        """计算方格行列数
        """
        recColCount = self.frameWidth / self.smallRectWidthInPix
        recRowCount = self.frameHeight / self.smallRectWidthInPix
        self.isLastColUnComplete = recColCount - int(recColCount) > 0
        self.isLastRowUnComplete = recRowCount - int(recRowCount) > 0
        self.rectColCount = int(recColCount) + (1 if self.isLastColUnComplete else 0)
        self.rectRowCount = int(recRowCount) + (1 if self.isLastRowUnComplete else 0)

    def getRectsPosition(self, rowIndex, colIndex):
        """计算给定行列坐标的方格像素坐标
        """
        rowIndex = int(max(min(rowIndex, self.rectRowCount - 1), 0))
        colIndex = int(max(min(colIndex, self.rectColCount - 1), 0))

        ltx, lty = self.smallRectWidthInPix * colIndex, self.smallRectWidthInPix * rowIndex
        rbx = min(self.frameWidth, self.smallRectWidthInPix * (colIndex + 1))
        rby = min(self.frameHeight, self.smallRectWidthInPix * (rowIndex + 1))

        return ((ltx, lty), (rbx, rby))
    
    def reCapVideo(self):
        """重新获取视频句柄
        """
        self.cap.release()
        self.cap = cv2.VideoCapture(self.sourceVideoFileName)
        self.initVideoInfo()
        self.smallRectWidthInPix = min(self.smallRectWidthInPix, self.frameHeight, self.frameWidth)
        self.initRectsInfo()

    def readVideoImage(self):
        """读取当前视频图像
        """
        return self.cap.read()[1]

    def getVideoSize(self):
        """获取视频大小
        """
        return (self.frameWidth, self.frameHeight)

    def release(self):
        self.cap.release()
