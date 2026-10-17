import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0061.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
print(len(fr))
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr]
win=cv2.createHanningWindow((1920,1080),cv2.CV_32F)
for i in [0,20,36,40,44,48,56,70]:
    print('shift',i,np.round(cv2.phaseCorrelate(g[70],g[i],win)[0],1))
res=[]
for i in range(30,62):
    hsv=cv2.cvtColor(fr[i],cv2.COLOR_BGR2HSV)
    # acorn body: bright white/light grey, low saturation, V>180 ; mesh is grey too... use V>200 & S<40
    m=((hsv[:,:,2]>195)&(hsv[:,:,1]<45)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4]); x,y,w,h,ar=st[k]
    res.append((i,x,x+w,y,y+h,cen[k][0],cen[k][1],ar))
    print(i,'x %d-%d y %d-%d w %d h %d cx %.1f cy %.1f area %d'%(x,x+w,y,y+h,w,h,cen[k][0],cen[k][1],ar))
