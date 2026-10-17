import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0054.mp4')
fr={};k=0
while True:
    ok,f=c.read()
    if not ok: break
    if k in (0,93,30,60): fr[k]=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32)
    k+=1
for name,(y0,y1,x0,x1) in {'bench34':(950,1100,1850,2480),'building':(100,700,100,1700),'hedgeR':(800,1100,2900,3700)}.items():
    for a,b in [(0,93)]:
        (dx,dy),r=cv2.phaseCorrelate(fr[a][y0:y1,x0:x1],fr[b][y0:y1,x0:x1]); print(name,a,b,'shift %.2f %.2f resp %.2f'%(dx,dy,r))
