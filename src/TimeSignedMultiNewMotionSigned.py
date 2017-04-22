import cv2
import numpy as np
import copy
import random
from PIL import Image
import time

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


#获取已剔除静止镜头的源视频为cap
cap = cv2.VideoCapture(sourceVideoFileName)

#获取源视频的帧大小、帧数和帧率
frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = float(cap.get(cv2.CAP_PROP_FPS))

#初始化每一帧的动作位置数组
motionLocation = [[False, False] for i in range(frameCount)]
#释放源视频
cap.release()

#获取完整源视频以计算平均帧
cap = cv2.VideoCapture(sourceVideoFileName)

#完整源视频的帧数
fullFrameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

#初始化平均帧，从视频首帧开始
_,resAve = cap.read()

#取无静止镜头的五分之一参与平均帧计算
resAve = np.float32(resAve) / (fullFrameCount / 5)
for fr in range(4, fullFrameCount - 1, 5):
    _, a = cap.read()
    a = np.float32(a)
    resAve = resAve + a / (fullFrameCount / 5)
resAve = np.uint8(resAve)

cap.release()

# cv2.imshow("ave", resAve)
# cv2.waitKey()

#再次获取已剔除静止镜头的源视频作为处理基础
cap = cv2.VideoCapture(sourceVideoFileName)

#限定画面划分为24列十四行
recCol = 24
recRow = 14
smallRecsCount = recCol * recRow

#生成小方格矩阵，每个元素是含有左上和右下两个坐标的tuple ((ltx, lty),(rbx, rby))
smallRecs = []
for i in range(recCol):
    tempRow =[]
    for j in range(recRow):
        tempRow.append(((i * 16,j * 16),((i + 1) * 16,(j + 1) * 16)))
    smallRecs.append(tempRow)

#初始化每一帧的图像数组
imgs = []
_, tmpIm = cap.read()
im = copy.copy(tmpIm)
imgs.append(tmpIm)
for i in range(frameCount - 1):
    _, tmpIm = cap.read()
    imgs.append(tmpIm)

#单线程操作
threadCount = 1

#尝试着线程结果合并需要的参数
imgdifPart = [[] for i in range(threadCount)]
imgdiffs = []
imgdiff = copy.deepcopy(resAve)
unFinished = [threadCount]

#函数，处理一部分视频区间的动作检测
def partProcess(partSt, partEnd, no):
    for i in range(int(len(imgs) * partSt), int(len(imgs) * partEnd)):
        moveRec = [] #存储存在动作的方格
        cv2.absdiff(imgs[i], resAve, imgdiff) #获取差值绝对值图像
        imgdifPart[no].append(copy.copy(imgdiff)) #差值图像存入该线程的差值图像库数组

        #检测存在动作的方格，并以方格索引的方式存入moveRec tuple(colIndex, rowIndex)
        for colIndex in range(len(smallRecs)):
            for rowIndex in range(len(smallRecs[0])):
                if judgeMoving(imgdiff, smallRecs[colIndex][rowIndex]):
                    moveRec.append((colIndex, rowIndex))
                    if colIndex > 11:
                        motionLocation[i][1] = True
                    else:
                        motionLocation[i][0] = True
        #绘制存在动作的方格
        for recIndex in moveRec:
            cv2.rectangle(imgs[i], smallRecs[recIndex[0]][recIndex[1]][0], smallRecs[recIndex[0]][recIndex[1]][1],
                          (0, 0, 255), thickness=1)
        #计算完成速度并显示
        finishRate = i / len(imgs) * 100
        print(("\rMotion Detection Processing: %4.2f %%\t" % finishRate) + "▋" * int(finishRate/5), end='') if i & 15 == 0 else 0
    
    #未完成线程数递减
    unFinished[0] -= 1
    print("\rMotion Detection Processing:  100%\t", "▋" * 20, "\nMotion Detection Finished, Video Generating...")

import threading
# for i in range(threadCount):
#     threading._start_new_thread(partProcess, ((1 / threadCount) * i, (1 / threadCount) * (i + 1), i))

# 等待线程全部完成
# while(unFinished[0] > 0):
#     time.sleep(1)

partProcess(0,1,0)
#合并差值绝对值图像集合
for i in range(threadCount):
    imgdiffs.extend(imgdifPart[i])

#下沉并拼接的函数
def cutMoveSide(newPos, inImgs, i, fromImgs, side):
    if side == 'L':
        inImgs[newPos][0:len(imgs[0]), 0: int(len(imgs[0][0])/2)] = fromImgs[i][0:len(imgs[0]), 0: int(len(imgs[0][0])/2)]
        cv2.putText(inImgs[newPos], "ORIGIN: " + str(int(i / fps / 60)) + " : " + (str(int(i / fps % 60))),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75 , (0,0,255),2)
    else:
        inImgs[newPos][0:len(imgs[0]), int(len(imgs[0][0]) / 2): int(len(imgs[0][0]))] = fromImgs[i][0:len(imgs[0]), int(len(imgs[0][0]) / 2): int(len(imgs[0][0]))]
        cv2.putText(inImgs[newPos], "ORIGIN: " + str(int(i / fps / 60)) + " : " + (str(int(i / fps % 60))), (200, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)


#初始化左右侧长度
leftLength = 0
rightLength = 0

#统计左右侧长度
newPos = 0
for i in range(len(imgs)):
    if motionLocation[i][0]:
        cutMoveSide(newPos, imgs, i, imgs, 'L')
        newPos+=1
    # print("fp", i)
leftLength = newPos

newPos = 0
for i in range(len(imgs)):
    if motionLocation[i][1]:
        cutMoveSide(newPos, imgs, i, imgs, 'R')
        newPos+=1
    # print("fp", i)
rightLength = newPos

#用平均帧填充剩余空白
newLength = rightLength if rightLength > leftLength else leftLength
if newLength > leftLength:
    for i in range(leftLength, newLength):
        cutMoveSide(i, imgs, 0, [resAve], 'L')
else:
    for i in range(rightLength, newLength):
        cutMoveSide(i,imgs,  0, [resAve], 'R')

#新建媒体文件写入参数
fcc = cv2.VideoWriter_fourcc('X','V','I','D')
writer = cv2.VideoWriter(outPutDifFileName, fcc, 25.0, (384,224))
writerRes = cv2.VideoWriter(outPutVideoFileName, fcc, 25.0, (384,224))

for i in range(newLength):
    writerRes.write(imgs[i])

for i in range(len(imgdiffs)):
    writer.write(imgdiffs[i])

writer.release()
writerRes.release()

print(fps, frameCount, frameHeight, frameWidth)
# print(motionLocation)
print("All Run Time: ", time.time() - startTime)
input()