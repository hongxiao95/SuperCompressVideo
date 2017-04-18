import cv2
import numpy as np
import copy
import random
from PIL import Image

def judgeMoving(img, rec):
    recTotalNumber0 = 0
    recTotalNumber1 = 0
    recTotalNumber2 = 0

    for i in range(rec[0][1], rec[1][1],3):
        for j in range(rec[0][0], rec[1][0], 3):
                recTotalNumber0 += img[i][j][0]
                recTotalNumber1 += img[i][j][1]
                recTotalNumber2 += img[i][j][2]

    return (recTotalNumber0 + recTotalNumber1 + recTotalNumber2) / 3 > 16 * 16 * 35 / 9

cap = cv2.VideoCapture("SourceVideo2.mp4")

frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = float(cap.get(cv2.CAP_PROP_FPS))
motionLocation = [[False, False] for i in range(frameCount)]

cap.release()


cap = cv2.VideoCapture("SourceVideo2.mp4")
fullFrameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

_,resAve = cap.read()
resAve = np.float32(resAve) / (fullFrameCount / 5)
for fr in range(4, fullFrameCount - 1, 5):
    _, a = cap.read()
    a = np.float32(a)
    resAve = resAve + a / (fullFrameCount / 5)
resAve = np.uint8(resAve)
cap.release()

cv2.imshow("ave", resAve)
cv2.waitKey()
cap = cv2.VideoCapture("SourceVideo2.mp4")

recCol = 24
recRow = 14
smallRecsCount = recCol * recRow
smallRecs = []
for i in range(recCol):
    tempRow =[]
    for j in range(recRow):
        tempRow.append(((i * 16,j * 16),((i + 1) * 16,(j + 1) * 16)))
    smallRecs.append(tempRow)


imgs = []
_, tmpIm = cap.read()
im = copy.copy(tmpIm)
imgs.append(tmpIm)
for i in range(frameCount - 1):
    _, tmpIm = cap.read()
    imgs.append(tmpIm)

threadCount = 1

imgdifPart = [[] for i in range(threadCount)]
imgdiffs = []
imgdiff = copy.deepcopy(resAve)
unFinished = [threadCount]

def partProcess(partSt, partEnd, no):
    for i in range(int(len(imgs)* partSt), int(len(imgs) * partEnd)):
        moveRec = []
        cv2.absdiff(imgs[i], resAve, imgdiff)
        imgdifPart[no].append(copy.copy(imgdiff))
        for colIndex in range(len(smallRecs)):
            for rowIndex in range(len(smallRecs[0])):
                if judgeMoving(imgdiff, smallRecs[colIndex][rowIndex]):
                    moveRec.append((colIndex, rowIndex))
                    if colIndex > 11:
                        motionLocation[i][1] = True
                    else:
                        motionLocation[i][0] = True
        for recIndex in moveRec:
            cv2.rectangle(imgs[i], smallRecs[recIndex[0]][recIndex[1]][0], smallRecs[recIndex[0]][recIndex[1]][1],
                          (0, 0, 255), thickness=2)
        print("fp", i / len(imgs) * 100, "%")
    unFinished[0] -= 1

import threading
import time
for i in range(threadCount):
    threading._start_new_thread(partProcess, ((1 / threadCount) * i, (1 / threadCount) * (i + 1), i))

while(unFinished[0] > 0):
    time.sleep(1)

for i in range(threadCount):
    imgdiffs.extend(imgdifPart[i])

#下沉并拼接
def cutMoveSide(newPos, inImgs, i, fromImgs, side):
    if side == 'L':
        inImgs[newPos][0:len(imgs[0]), 0: int(len(imgs[0][0])/2)] = fromImgs[i][0:len(imgs[0]), 0: int(len(imgs[0][0])/2)]
    else:
        inImgs[newPos][0:len(imgs[0]), int(len(imgs[0][0]) / 2): int(len(imgs[0][0]))] = fromImgs[i][0:len(imgs[0]), int(len(imgs[0][0]) / 2): int(len(imgs[0][0]))]

leftLength = 0
rightLength = 0

newPos = 0
for i in range(len(imgs)):
    if motionLocation[i][0]:
        cutMoveSide(newPos, imgs, i, imgs, 'L')
        newPos+=1
    print("fp", i)
leftLength = newPos

newPos = 0
for i in range(len(imgs)):
    if motionLocation[i][1]:
        cutMoveSide(newPos, imgs, i, imgs, 'R')
        newPos+=1
    print("fp", i)
rightLength = newPos

newLength = rightLength if rightLength > leftLength else leftLength
if newLength > leftLength:
    for i in range(leftLength, newLength):
        cutMoveSide(i, imgs, 0, [resAve], 'L')
else:
    for i in range(rightLength, newLength):
        cutMoveSide(i,imgs,  0, [resAve], 'R')


fcc = cv2.VideoWriter_fourcc('X','V','I','D')
writer = cv2.VideoWriter("Diff.avi", fcc, 25.0, (384,224))
writerRes = cv2.VideoWriter("Res.avi", fcc, 25.0, (384,224))
for i in range(newLength):
    writerRes.write(imgs[i])

for i in range(len(imgdiffs)):
    writer.write(imgdiffs[i])

writer.release()
writerRes.release()

print(fps, frameCount, frameHeight, frameWidth)
print(motionLocation)