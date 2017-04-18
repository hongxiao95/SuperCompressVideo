import cv2
import numpy as np
import copy
import random
from PIL import Image

def calcTotalDiff(img1, img2, rec):
    imgATotalNumber = 0
    imgBTotalNUmber = 0
    for i in range(rec[0][0], rec[0][1],3):
        for j in range(rec[1][0], rec[1][1], 3):
            for c in range(1):
                c = random.randint(0,2)
                imgATotalNumber += img1[i][j][c]
                imgBTotalNUmber += img2[i][j][c]
    return abs(imgBTotalNUmber - imgATotalNumber)

def newCalcTotalDiff(img1, img2, rec):
    imgATotalNumber = 0
    imgBTotalNUmber = 0
    for i in range(rec[0][0], rec[0][1],3):
        for j in range(rec[1][0], rec[1][1], 3):
            for c in range(1):
                c = random.randint(0,2)
                imgATotalNumber += img1[i][j][c]
                imgBTotalNUmber += img2[i][j][c]
    return abs(imgBTotalNUmber - imgATotalNumber)

cap = cv2.VideoCapture("SourceVideo.mp4")

frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = float(cap.get(cv2.CAP_PROP_FPS))

_,resAve = cap.read()
resAve = np.float32(resAve) / frameCount
for fr in range(frameCount - 1):
    _, a = cap.read()
    a = np.float32(a)
    resAve = resAve + a/frameCount
resAve = np.uint8(resAve)
cap.release()
cv2.imshow("ave", resAve)
cv2.waitKey()
cap = cv2.VideoCapture("SourceVideo2.mp4")

smallRecsCount = 12*7
smallRecs = []
for i in range(12):
    tempRow =[]
    for j in range(7):
        tempRow.append(((i * 32,j * 32),((i + 1) * 32,(j + 1) * 32)))
    smallRecs.append(tempRow)


imgs = []
_, tmpIm = cap.read()
im = copy.copy(tmpIm)
imgs.append(tmpIm)
for i in range(frameCount - 1):
    _, tmpIm = cap.read()
    imgs.append(tmpIm)

imgdiffs = []
imgdiff = copy.deepcopy(resAve)
for i in range(len(imgs)):
    moveRec = []
    for colIndex in range(len(smallRecs)):
        for rowIndex in range(len(smallRecs[0])):
            diff = calcTotalDiff(imgs[i], resAve, smallRecs[colIndex][rowIndex])
            if diff > 32 * 32 / 9 * 3:
                moveRec.append((colIndex, rowIndex))
    # for recIndex in moveRec:
    #     cv2.rectangle(imgs[i], smallRecs[recIndex[0]][recIndex[1]][0], smallRecs[recIndex[0]][recIndex[1]][1], (0,0,255), thickness=2)
    cv2.absdiff(imgs[i], resAve, imgdiff)
    imgdiffs.append(copy.copy(imgdiff))
    # cv2.imshow("hh",imgdiff)
    # cv2.waitKey()
#    input()
    print("fp", i / len(imgs) * 100,"%" )

fcc = cv2.VideoWriter_fourcc('X','V','I','D')
writer = cv2.VideoWriter("get.avi", fcc, 25.0, (384,288))
for i in range(0,110):
    writer.write(imgdiffs[i])
writer.release()


print(fps, frameCount, frameHeight, frameWidth)
