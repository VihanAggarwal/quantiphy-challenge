import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0047.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr]
# camera motion via phase correlation on bottom strip (rows 700-1080) vs frame 29
ref=g[29]
win=cv2.createHanningWindow((1920,380),cv2.CV_32F)
sh=[]
for i in range(len(g)):
    (dx,dy),r=cv2.phaseCorrelate(ref[700:1080],g[i][700:1080],win)
    sh.append((dx,dy))
sh=np.array(sh); print('shifts',np.round(sh,1).tolist())
# ball: dark orange/brown; use HSV: red-ish hue, saturation>?; ball vs floor (light wood) and red lines (dark maroon)
res=[]
for i,f in enumerate(fr):
    M=np.float32([[1,0,-sh[i,0]],[0,1,-sh[i,1]]])
    a=cv2.warpAffine(g[i],M,(1920,1080))
    d=np.abs(a-ref)
    m=(d>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); x,y,w,h,ar=st[k]
        res.append((i,cen[k][0],cen[k][1],x,y,w,h,ar))
        print(i,'cx %.1f cy %.1f x %d-%d y %d-%d w %d h %d area %d'%(cen[k][0],cen[k][1],x,x+w,y,y+h,w,h,ar))
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/t47.npy',np.array(res))
