import cv2, numpy as np
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work/'
bg=cv2.imread(W+'bg.png'); g=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY)
lsd=cv2.createLineSegmentDetector(0)
L=lsd.detect(g)[0].reshape(-1,4)
segs=[]
for x1,y1,x2,y2 in L:
    dx,dy=x2-x1,y2-y1; ln=np.hypot(dx,dy)
    if ln<120: continue
    ang=np.degrees(np.arctan2(abs(dx),abs(dy)))
    if ang<12: segs.append((x1,y1,x2,y2,ln))
segs=np.array(segs)
print(len(segs))
for s in segs[np.argsort(-segs[:,4])][:40]: print(np.round(s,1))
np.save(W+'vsegs.npy',segs)
vis=bg.copy()
for x1,y1,x2,y2,l in segs: cv2.line(vis,(int(x1),int(y1)),(int(x2),int(y2)),(0,0,255),3)
cv2.imwrite(W+'vsegs.png',cv2.resize(vis,(1280,720)))
