import cv2 as cv
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import pyautogui


wCam=1280
hCam=720
frameR=100
smoothening=10

prevY = 0
scrollCooldown = 0.1  # 100ms delay between scrolls
lastScrollTime = time.time()

plocX,plocY=0,0
clocX,clocY=0,0

cap=cv.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime=0
detector=htm.handDetector(maxHands=1)
wScr,hScr=autopy.screen.size()
print(wScr,hScr)

while True:
    success,img=cap.read()
    img = cv.flip(img, 1)
    img=detector.findHands(img)
    lmList,bbox=detector.findPosition(img)

    if len(lmList)!=0:
        x1,y1 = lmList[4][1:]
        x2,y2=lmList[8][1:]
        x4, y4 = lmList[12][1:]

        fingers=detector.fingersUp()
        cv.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        if fingers[1]==1 and sum(fingers)==1:
            x3=np.interp(x2,(6*frameR,wCam-2*frameR),(0,wScr))
            y3 = np.interp(y2, (2*frameR, hCam-3*frameR), (0, hScr))

            clocX=plocX + (x3 - plocX) / smoothening
            clocY=plocY + (y3 - plocY) / smoothening

            autopy.mouse.move(clocX,clocY)
            cv.circle(img,(x2,y2),15,(255,0,255),cv.FILLED)
            plocX,plocY=clocX,clocY

        if fingers[1] == 1 and fingers[0]==1:
            length,img,lineInfo=detector.findDistance(4,8,img)
            if length<40:
                cv.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv.FILLED)
                autopy.mouse.click()

        if fingers[1] == 1 and fingers[2] == 1 and sum(fingers) == 2:
            avgY = (y2 + y4) // 2
            currentTime = time.time()
            # Check if enough time has passed since the last scroll
            if prevY != 0 and (currentTime - lastScrollTime) > scrollCooldown:
                if avgY>hScr:
                    pyautogui.scroll(-150)  # Scroll down
                    lastScrollTime = currentTime
                if avgY < prevY - 10:  # Hand moved up
                    pyautogui.scroll(-150)  # Scroll down
                    lastScrollTime = currentTime
                elif avgY > prevY + 10:  # Hand moved down

                    pyautogui.scroll(150)  # Scroll up
                    lastScrollTime = currentTime

            prevY = avgY  # Update the previous Y position

    cTime=time.time()
    fps=1/(cTime-pTime)
    pTime=cTime
    cv.putText(img,str(int(fps)),(20,50),cv.FONT_HERSHEY_DUPLEX,2,(255,0,0))

    cv.imshow("Itrack",img)
    cv.waitKey(1)
