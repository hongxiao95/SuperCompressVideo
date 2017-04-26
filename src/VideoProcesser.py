import cv2
import numpy as np
from PIL import Image
import copy
import MyVideo

class VideoProcesser(object):
    LEFT_MOTION = 2
    RIGHT_MOTION = 1
    BOTH_MOTON = 3
    NO_MOTION = 0

    def __init__(self):
        pass

    @classmethod
    def judgeMoving(cls, imgDiff, rec):
        """判断给定方格内是否存在运动的函数

        Args:
            imgDiff: 预处理过的存储着与平均帧差值的差值帧
            rec: 存储着给定方格的左上和右下坐标的tuple((ltx, lty),(rbx, rby))

        Returns:
            返回是否存在运动的bool值
        """
        recTotalPixValue = 0
        for i in range(rec[0][1], rec[1][1],3):
            for j in range(rec[0][0], rec[1][0], 3):
                    recTotalPixValue += imgDiff[i][j][j % 3]
        return recTotalPixValue > abs(rec[0][1] - rec[1][1]) * abs(rec[1][0] - rec[0][0]) * 4    #1023 means 16 * 16 * 4  means 16 * 16 * 35 / 3(rgb) / 3(skiped pix)

    @classmethod
    def detectAndSignMotions(cls, videoImages, videoAverageImage, videoDiffImages, sourceVideo, motionSides):
        """检测动作并绘制红方格
        Args:
            videoImages: 存储着原始视频的图像集合
            videoAverageImage: 平均帧 （背景帧）
            videoDiffImages: 差值帧集合的空数组
            smallRects: 记载着第n行第n列的小方格坐标的数组
            motionSides: 用来记载动作发生在左右哪边的数组
        
        Returns:
            void
        """
        print()
        for i in range(len(videoImages)):
            moveRec = [] #存储存在动作的方格
            diffImage = np.array(videoAverageImage)
            cv2.absdiff(videoImages[i], videoAverageImage, diffImage) #获取差值绝对值图像
            videoDiffImages.append(copy.copy(diffImage)) #差值图像存入该线程的差值图像库数组

            #检测存在动作的方格，并以方格索引的方式存入moveRec tuple(colIndex, rowIndex)
            for colIndex in range(sourceVideo.rectColCount):
                for rowIndex in range(sourceVideo.rectRowCount):
                    if cls.judgeMoving(diffImage, sourceVideo.getRectsPosition(rowIndex, colIndex)):
                        moveRec.append((rowIndex, colIndex))
                        if colIndex > int(sourceVideo.rectColCount / 2):
                            motionSides[i] |= VideoProcesser.RIGHT_MOTION
                        else:
                            motionSides[i] |= VideoProcesser.LEFT_MOTION
            #绘制存在动作的方格
            for recIndex in moveRec:
                cv2.rectangle(videoImages[i], sourceVideo.getRectsPosition(recIndex[0],recIndex[1])[0], sourceVideo.getRectsPosition(recIndex[0],recIndex[1])[1],
                            (0, 0, 255), thickness=1)
            #计算完成速度并显示
            finishRate = i / len(videoImages) * 100
            print(("\rMotion Detection Processing: %4.2f %%\t" % finishRate) + "▋" * int(finishRate/5), end='') if i & 15 == 0 else 0

        print("\rMotion Detection Processing:  100%\t", "▋" * 20, "\nMotion Detection Finished, Video Generating...")

    @classmethod
    def cutMoveSide(cls, newPos, intoImgs, oldPos, fromImgs, side, fps):
        """将有动作的半画面下沉拼接
        
        Args:
            newPos: 画面下沉后拼接至的新帧序号
            intoImgs: 画面拼接至的帧集
            oldPos: 需要拼接的画面的原位置
            fromImgs: 获取源图像的帧集
            side: 哪一边需要下沉，取值为 'L' 或 'R'
            fps: 视频帧率
        
        Returns:
            void
        """
        if bool(side & VideoProcesser.LEFT_MOTION):
            intoImgs[newPos][0:len(intoImgs[0]), 0: int(len(intoImgs[0][0])/2)] = fromImgs[oldPos][0:len(fromImgs[0]), 0: int(len(fromImgs[0][0])/2)]
            cv2.putText(intoImgs[newPos], "ORIGIN: " + str(int(oldPos / fps / 60)) + " : " + (str(int(oldPos / fps % 60))),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75 , (0,0,255),2)
        else:
            intoImgs[newPos][0:len(intoImgs[0]), int(len(intoImgs[0][0]) / 2): int(len(intoImgs[0][0]))] = fromImgs[oldPos][0:len(fromImgs[0]), int(len(fromImgs[0][0]) / 2): int(len(fromImgs[0][0]))]
            cv2.putText(intoImgs[newPos], "ORIGIN: " + str(int(oldPos / fps / 60)) + " : " + (str(int(oldPos / fps % 60))), (200, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
