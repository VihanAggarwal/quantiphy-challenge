import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0048.mp4')
frames=[]
while True:
    ok,f=cap.read()
    if not ok: break
    frames.append(f)
# camera drift via phase correlation on upper wall strip relative to frame 0
g0=cv2.cvtColor(frames[0],cv2.COLOR_BGR2GRAY).astype(np.float32)
win=cv2.createHanningWindow((1920-200,300),cv2.CV_32F)
drift=[]
for i,f in enumerate(frames):
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32)
    # use region rows 820-1080 (floor/baseboard) and top rows? use baseboard strip rows 500-800 excluding ball? use full but whatever
    a=g0[520:820,100:1820]; b=g[520:820,100:1820]
    (dx,dy),r=cv2.phaseCorrelate(a,b,win)
    drift.append((dx,dy))
drift=np.array(drift)
np.set_printoptions(precision=2,suppress=True)
print('drift every 10:',drift[::10])
bg=frames[10]
for i in range(30,66):
    f=frames[i]
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    # ball dark red: hue <15 or >165, sat>80, val<170
    h,s,v=hsv[:,:,0],hsv[:,:,1],hsv[:,:,2]
    m=(((h<14)|(h>165))&(s>110)&(v<190)&(v>40)).astype(np.uint8)
    m[880:,:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); x,y,w,hh,a=st[k]
        print(i, 'bbox',x,y,w,hh,'a',a,'cen',np.round(cen[k],1),'drift',np.round(drift[i],1))
