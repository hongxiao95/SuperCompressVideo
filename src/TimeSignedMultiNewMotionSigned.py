import cv2
import numpy as np
import copy
import random
from PIL import Image
import time

'''
重构步骤：
1、迁移函数定义、去除多线程部分 OK
2、移除函数外部变量依赖 OK
3、剥离函数到模块文件
4、撰写文档字符串注释
5、规范化定义等的位置
6、输入输出视频画面大小的一般化
7、主函数参数化调用
'''

sourceVideoFileName = r"../SourceVideos/SourceVideo2.mp4"
outPutVideoFileName = r"../OutputVideos/Output1.avi"
outPutDifFileName = r"../OutputVideos/Diff1.avi"

#标记起始时间
startTime = time.time()


#判断给定方格内是否有运动的函数
def judgeMoving(img, rec):
    recTotalNumber = 0
    for i in range(rec[0][1], rec[1][1],3):
        for j in range(rec[0][0], rec[1][0], 3):
                recTotalNumber += img[i][j][j % 3]
    return recTotalNumber > 16 * 16 * 4
#1023 means 16 * 16 * 4  means 16 * 16 * 35 / 3(rgb) / 3(skiped pix)


#检测动作并绘制红方格
def detectAndSignMotions(videoImages, videoAverageImage, videoDiffImages, smallRects, motionSides):
    for i in range(len(videoImages)):
        moveRec = [] #存储存在动作的方格
        diffImage = np.array(videoAverageImage)
        cv2.absdiff(videoImages[i], videoAverageImage, diffImage) #获取差值绝对值图像
        videoDiffImages.append(copy.copy(diffImage)) #差值图像存入该线程的差值图像库数组

        #检测存在动作的方格，并以方格索引的方式存入moveRec tuple(colIndex, rowIndex)
        for colIndex in range(len(smallRects)):
            for rowIndex in range(len(smallRects[0])):
                if judgeMoving(diffImage, smallRects[colIndex][rowIndex]):
                    moveRec.append((colIndex, rowIndex))
                    if colIndex > 11:
                        motionSides[i][1] = True
                    else:
                        motionSides[i][0] = True
        #绘制存在动作的方格
        for recIndex in moveRec:
            cv2.rectangle(videoImages[i], smallRects[recIndex[0]][recIndex[1]][0], smallRects[recIndex[0]][recIndex[1]][1],
                          (0, 0, 255), thickness=1)
        #计算完成速度并显示
        finishRate = i / len(videoImages) * 100
        print(("\rMotion Detection Processing: %4.2f %%\t" % finishRate) + "▋" * int(finishRate/5), end='') if i & 15 == 0 else 0
    
    print("\rMotion Detection Processing:  100%\t", "▋" * 20, "\nMotion Detection Finished, Video Generating...")


#下沉并拼接的函数
def cutMoveSide(newPos, inImgs, i, fromImgs, side):
    if side == 'L':
        inImgs[newPos][0:len(videoImgs[0]), 0: int(len(videoImgs[0][0])/2)] = fromImgs[i][0:len(videoImgs[0]), 0: int(len(videoImgs[0][0])/2)]
        cv2.putText(inImgs[newPos], "ORIGIN: " + str(int(i / fps / 60)) + " : " + (str(int(i / fps % 60))),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75 , (0,0,255),2)
    else:
        inImgs[newPos][0:len(videoImgs[0]), int(len(videoImgs[0][0]) / 2): int(len(videoImgs[0][0]))] = fromImgs[i][0:len(videoImgs[0]), int(len(videoImgs[0][0]) / 2): int(len(videoImgs[0][0]))]
        cv2.putText(inImgs[newPos], "ORIGIN: " + str(int(i / fps / 60)) + " : " + (str(int(i / fps % 60))), (200, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)



#获取源视频为cap
cap = cv2.VideoCapture(sourceVideoFileName)

#获取源视频的帧大小、帧数和帧率
frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = float(cap.get(cv2.CAP_PROP_FPS))

#初始化每一帧的动作位置数组
motionSides = [[False, False] for i in range(frameCount)]

#初始化平均帧，从视频首帧开始
_,videoAverageImage = cap.read()

#取视频五分之一参与平均帧计算
videoAverageImage = np.float32(videoAverageImage) / (frameCount / 5)
for fr in range(4, frameCount - 1, 5):
    _, a = cap.read()
    a = np.float32(a)
    videoAverageImage = videoAverageImage + a / (frameCount / 5)
videoAverageImage = np.uint8(videoAverageImage)

#限定画面划分为24列十四行
recCol = 24
recRow = 14
smallRecsCount = recCol * recRow


#小方格矩阵，每个元素是含有左上和右下两个坐标的tuple ((ltx, lty),(rbx, rby))
smallRects = []

for i in range(recCol):
    tempRow =[]
    for j in range(recRow):
        tempRow.append(((i * 16,j * 16),((i + 1) * 16,(j + 1) * 16)))
    smallRects.append(tempRow)

#重新获取视频对象
cap.release()
cap = cv2.VideoCapture(sourceVideoFileName)

#初始化每一帧的图像数组
videoImgs = []
_, tmpIm = cap.read()
im = copy.copy(tmpIm)
videoImgs.append(tmpIm)
for i in range(frameCount - 1):
    _, tmpIm = cap.read()
    videoImgs.append(tmpIm)

#尝试着线程结果合并需要的参数
videoDiffImages = []

detectAndSignMotions(videoImgs, videoAverageImage, videoDiffImages, smallRects, motionSides)

#初始化左右侧长度
leftLength = 0
rightLength = 0

#统计左右侧长度
newPos = 0
for i in range(len(videoImgs)):
    if motionSides[i][0]:
        cutMoveSide(newPos, videoImgs, i, videoImgs, 'L')
        newPos+=1
    # print("fp", i)
leftLength = newPos

newPos = 0
for i in range(len(videoImgs)):
    if motionSides[i][1]:
        cutMoveSide(newPos, videoImgs, i, videoImgs, 'R')
        newPos+=1
    # print("fp", i)
rightLength = newPos

#用平均帧填充剩余空白
newLength = rightLength if rightLength > leftLength else leftLength
if newLength > leftLength:
    for i in range(leftLength, newLength):
        cutMoveSide(i, videoImgs, 0, [videoAverageImage], 'L')
else:
    for i in range(rightLength, newLength):
        cutMoveSide(i,videoImgs,  0, [videoAverageImage], 'R')

#新建媒体文件写入参数
fcc = cv2.VideoWriter_fourcc('X','V','I','D')
writer = cv2.VideoWriter(outPutDifFileName, fcc, 25.0, (384,224))
writerRes = cv2.VideoWriter(outPutVideoFileName, fcc, 25.0, (384,224))

for i in range(newLength):
    writerRes.write(videoImgs[i])

for i in range(len(videoDiffImages)):
    writer.write(videoDiffImages[i])

writer.release()
writerRes.release()

print(fps, frameCount, frameHeight, frameWidth)
# print(motionLocation)
print("All Run Time: ", time.time() - startTime)
input()