import cv2
from PIL import Image
import numpy as np

class MyVideo(object):
    """MyVideo 类，封装过的openCv读取到的视频及一些常用操作
    """

    def __init__(self, sourceVideoFileName, smallRectWidthInPix):
        self.sourceVideoFileName = sourceVideoFileName
        self.captureVideo()
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
        
    def captureVideo(self):
        """封装的获取视频句柄"""
        self.cap = cv2.VideoCapture(self.sourceVideoFileName)
        self.currentFrameIndex = 0
    
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
        self.captureVideo()
        self.initVideoInfo()
        self.smallRectWidthInPix = min(self.smallRectWidthInPix, self.frameHeight, self.frameWidth)
        self.initRectsInfo()

    def readVideoImage(self):
        """读取当前视频图像
        """
        self.currentFrameIndex += 1
        return self.cap.read()[1]

    def getVideoSize(self):
        """获取视频大小
        """
        return (self.frameWidth, self.frameHeight)

    def release(self):
        """释放视频句柄
        """
        self.cap.release()
        self.currentFrameIndex = 0
    
    def getAverageFrame(self, calcRate, offOrOnPrintInfo = False):
        """计算平均帧
        """
        if self.currentFrameIndex != 0:
            self.reCapVideo()
        
        calcRate = min(1, calcRate)
        skippedEach = (1 / calcRate)

        averageFrame = np.float32(self.readVideoImage())
        tempImageCount = 1

        if offOrOnPrintInfo:
            finishRate = 1 / self.frameCount * 100
            print(("Getting Average Frame... %4.2f %%\t" % finishRate) +
              "▋" * int(finishRate / 5), end="")
        for i in range(1, self.frameCount):
            tmpFrame = self.readVideoImage()
            if i % skippedEach == 0:
                averageFrame += np.float32(tmpFrame)
                tempImageCount += 1
                if offOrOnPrintInfo:
                    finishRate = i / self.frameCount * 100
                    print("\r" + " " * 70 + ("\rGetting Average Frame... %4.2f %%\t" % 
                      finishRate) + "▋" * int(finishRate / 5), end="")
        
        averageFrame /= tempImageCount
        return np.uint8(averageFrame)
       
    def getFramesImageList(self):
        """获取所有图像的列表
        """
        if self.currentFrameIndex != 0:
            self.reCapVideo()
        
        framesImageList = []
        for i in range(self.frameCount):
            framesImageList.append(np.uint8(self.readVideoImage()))
        
        return framesImageList