import cv2
import numpy as np
import copy
import random
from PIL import Image
import time
import VideoProcesser
import MyVideo

'''
重构步骤：
1、迁移函数定义、去除多线程部分 OK
2、移除函数外部变量依赖 OK
3、剥离函数到模块文件 OK
4、撰写文档字符串注释 OK
5、规范化定义等的位置 OK
6、方格划分参数化
6、获取小方格坐标函数化
7、画面位置参数化
6、输入输出视频画面大小的一般化
7、主函数参数化调用
'''


def main():
    sourceVideoFileName = r"../SourceVideos/SourceVideo2.mp4"
    outPutVideoFileName = r"../OutputVideos/Output1.avi"
    outPutDifFileName = r"../OutputVideos/Diff1.avi"
    smallRectWidthInPix = 15

    startTime = time.time()     #标记起始时间
    cap = cv2.VideoCapture(sourceVideoFileName)     #获取源视频为cap
    frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))         #获取源视频的帧大小、帧数和帧率
    frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS))

    recColCount = frameWidth / smallRectWidthInPix     #计算画面应该被分为多少方格
    recRowCount = frameHeight / smallRectWidthInPix
    isLastColUnComplete = recColCount - int(recColCount) > 0
    isLastRowUnComplete = recRowCount - int(recRowCount) > 0
    recColCount = int(recColCount) + (1 if isLastColUnComplete else 0)
    recRowCount = int(recRowCount) + (1 if isLastRowUnComplete else 0)

    smallRects = []     #小方格矩阵，每个元素是含有左上和右下两个坐标的tuple ((ltx, lty),(rbx, rby))
    videoImgs = []      #初始化每一帧的图像数组
    videoDiffImages = []        #初始化差值图像数组

    for i in range(recCol):
        """生成小方格坐标数组"""
        tempRow =[]
        for j in range(recRow):
            tempRow.append(((i * 16,j * 16),((i + 1) * 16,(j + 1) * 16)))
        smallRects.append(tempRow)

    motionSides = [[False, False] for i in range(frameCount)]       #初始化每一帧的动作位置数组


    _,videoAverageImage = cap.read()        #初始化平均帧，从视频首帧开始
    videoAverageImage = np.float32(videoAverageImage) / (frameCount / 5)        #取视频前五分之一参与平均帧计算

    for fr in range(4, frameCount - 1, 5):
        """只取视频前五分之一计算平均帧"""
        _, a = cap.read()
        a = np.float32(a)
        videoAverageImage = videoAverageImage + a / (frameCount / 5)
    videoAverageImage = np.uint8(videoAverageImage)     #平均帧生成
 
    cap.release()       #重新获取视频对象，用于读取视频完整内容
    cap = cv2.VideoCapture(sourceVideoFileName)

    _, tmpIm = cap.read()       #准备读取完整视频内容
    im = copy.copy(tmpIm)
    videoImgs.append(tmpIm)
    for i in range(frameCount - 1):
        _, tmpIm = cap.read()
        videoImgs.append(tmpIm)

    """准备处理视频"""
    VideoProcesser.detectAndSignMotions(videoImgs, videoAverageImage, videoDiffImages, smallRects, motionSides)     #标记所有动作并绘制红框

    leftLength = 0      #初始化左右侧长度
    rightLength = 0

    
    newPos = 0      #统计左右侧长度并沉降有动作的帧
    for i in range(len(videoImgs)):
        if motionSides[i][0]:
            VideoProcesser.cutMoveSide(newPos, videoImgs, i, videoImgs, 'L', fps)
            newPos+=1
    leftLength = newPos
    newPos = 0
    for i in range(len(videoImgs)):
        if motionSides[i][1]:
            VideoProcesser.cutMoveSide(newPos, videoImgs, i, videoImgs, 'R', fps)
            newPos+=1
    rightLength = newPos

    newLength = rightLength if rightLength > leftLength else leftLength     #用平均帧填充剩余空白
    if newLength > leftLength:
        for i in range(leftLength, newLength):
            VideoProcesser.cutMoveSide(i, videoImgs, 0, [videoAverageImage], 'L', fps)
    else:
        for i in range(rightLength, newLength):
            VideoProcesser.cutMoveSide(i,videoImgs,  0, [videoAverageImage], 'R', fps)

    """新建媒体文件写入参数"""
    fcc = cv2.VideoWriter_fourcc('X','V','I','D')
    writer = cv2.VideoWriter(outPutDifFileName, fcc, fps, (frameWidth, frameHeight))
    writerRes = cv2.VideoWriter(outPutVideoFileName, fcc, fps, (frameWidth, frameHeight))

    for i in range(newLength):
        writerRes.write(videoImgs[i])

    for i in range(len(videoDiffImages)):
        writer.write(videoDiffImages[i])

    writer.release()
    writerRes.release()

    print(fps, frameCount, frameHeight, frameWidth)
    print("All Run Time: ", time.time() - startTime)
    input()


if __name__ == '__main__':
    main()