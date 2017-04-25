import cv2
import numpy as np
import copy
import random
from PIL import Image
import time
import VideoProcesser
from MyVideo import MyVideo

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
    startTime = time.time()     #标记起始时间

    sourceVideoFileName = r"../SourceVideos/SourceVideo2.mp4"
    outPutVideoFileName = r"../OutputVideos/Output1.avi"
    outPutDifFileName = r"../OutputVideos/Diff1.avi"
    smallRectWidthInPix = 16

    sourceVideo = MyVideo(sourceVideoFileName, smallRectWidthInPix)

    videoImgs = []      #初始化每一帧的图像数组
    videoDiffImages = []        #初始化差值图像数组
    motionSides = [[False, False] for i in range(sourceVideo.frameCount)]       #初始化每一帧的动作位置数组

    videoAverageImage = sourceVideo.getAverageFrame(0.2, True)     #平均帧生成
    videoImgs = sourceVideo.getFramesImageList()        #读取视频所有图像
    sourceVideo.release()

    """准备处理视频"""
    VideoProcesser.detectAndSignMotions(videoImgs, videoAverageImage, videoDiffImages, sourceVideo, motionSides)     #标记所有动作并绘制红框

    leftLength = 0      #初始化左右侧长度
    rightLength = 0

    
    newPos = 0      #统计左右侧长度并沉降有动作的帧
    for i in range(len(videoImgs)):
        if motionSides[i][0]:
            VideoProcesser.cutMoveSide(newPos, videoImgs, i, videoImgs, 'L', sourceVideo.fps)
            newPos+=1
    leftLength = newPos
    newPos = 0
    for i in range(len(videoImgs)):
        if motionSides[i][1]:
            VideoProcesser.cutMoveSide(newPos, videoImgs, i, videoImgs, 'R', sourceVideo.fps)
            newPos+=1
    rightLength = newPos

    newLength = rightLength if rightLength > leftLength else leftLength     #用平均帧填充剩余空白
    if newLength > leftLength:
        for i in range(leftLength, newLength):
            VideoProcesser.cutMoveSide(i, videoImgs, 0, [videoAverageImage], 'L', sourceVideo.fps)
    else:
        for i in range(rightLength, newLength):
            VideoProcesser.cutMoveSide(i,videoImgs,  0, [videoAverageImage], 'R', sourceVideo.fps)

    """新建媒体文件写入参数"""
    fcc = cv2.VideoWriter_fourcc('X','V','I','D')
    writer = cv2.VideoWriter(outPutDifFileName, fcc, sourceVideo.fps, sourceVideo.getVideoSize())
    writerRes = cv2.VideoWriter(outPutVideoFileName, fcc, sourceVideo.fps, sourceVideo.getVideoSize())

    for i in range(newLength):
        writerRes.write(videoImgs[i])

    for i in range(len(videoDiffImages)):
        writer.write(videoDiffImages[i])

    writer.release()
    writerRes.release()

    print(sourceVideo.fps, sourceVideo.frameCount, sourceVideo.frameHeight, sourceVideo.frameWidth)
    print("All Run Time: ", time.time() - startTime)
    input()


if __name__ == '__main__':
    main()