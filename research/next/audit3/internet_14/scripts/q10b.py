import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0010.mp4')
F={}
k=0
while True:
    ok,im=c.read()
    if not ok: break
    if 46<=k<=80: F[k]=im
    k+=1
T=F[75][959-30:959+30,2157-30:2157+30]
# refine: find ball center in f75 by matching small disc
pos={}
prev=np.array([2157.,959.])
for k in range(75,46,-1):
    im=F[k]
    x0=int(prev[0]-140); y0=int(prev[1]-140)
    R=im[max(0,y0):y0+280, max(0,x0):x0+280]
    r=cv2.matchTemplate(R,T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
    p=np.array([max(0,x0)+ml[0]+30, max(0,y0)+ml[1]+30],float)
    pos[k]=(p,mv); prev=p
prev=np.array([2157.,959.])
for k in range(76,81):
    im=F[k]; x0=int(prev[0]-140); y0=int(prev[1]-140)
    R=im[max(0,y0):y0+280, max(0,x0):x0+280]
    r=cv2.matchTemplate(R,T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
    p=np.array([max(0,x0)+ml[0]+30, max(0,y0)+ml[1]+30],float); pos[k]=(p,mv); prev=p
for k in sorted(pos): print(k, pos[k][0], round(pos[k][1],2))
# camera shift: register frames to frame 60 on the building band using ECC translation
g60=cv2.cvtColor(F[60][1150:1500,:],cv2.COLOR_BGR2GRAY).astype(np.float32)
for k in (50,55,58,59,61,62,65,70):
    g=cv2.cvtColor(F[k][1150:1500,:],cv2.COLOR_BGR2GRAY).astype(np.float32)
    print('cam rel60',k,cv2.phaseCorrelate(g60,g))
