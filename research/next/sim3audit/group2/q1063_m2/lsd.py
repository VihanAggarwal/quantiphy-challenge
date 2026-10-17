import cv2, numpy as np
bg=cv2.imread('bg.png'); g=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY)
lsd=cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
lines=np.asarray(lsd.detect(g)[0]).reshape(-1,4)
L=[]
for x1,y1,x2,y2 in lines:
    l=np.hypot(x2-x1,y2-y1)
    if l<40: continue
    mx,my=(x1+x2)/2,(y1+y2)/2
    if not (1020<mx<1900 and 780<my<1420): continue
    ang=np.degrees(np.arctan2(y2-y1,x2-x1))
    if ang<-90: ang+=180
    if ang>90: ang-=180
    L.append((x1,y1,x2,y2,l,ang,mx,my))
L=np.array(L)
np.save('lsd_house.npy',L)
for r in sorted(L.tolist(), key=lambda r:r[5]):
    print(' '.join(f'{v:8.1f}' for v in r))
