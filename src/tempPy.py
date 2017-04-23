def partProcess(videoImgs, videoAverageImages, diffImages, smallRects, motionSides):
    for i in range(len(imgs)):
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
