import cv2,numpy as np
med=cv2.imread('median0053.png')
g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY)
lsd=cv2.createLineSegmentDetector()
L=lsd.detect(g)[0].reshape(-1,4)
lens=np.hypot(L[:,2]-L[:,0],L[:,3]-L[:,1])
L=L[lens>60]; lens=lens[lens>60]
ang=np.degrees(np.arctan2(L[:,3]-L[:,1],L[:,2]-L[:,0]))%180
vis=med.copy()
for (x1,y1,x2,y2),a,l in sorted(zip(L,ang,lens),key=lambda t:-t[2]):
    print(f'{x1:7.1f} {y1:6.1f} {x2:7.1f} {y2:6.1f} ang {a:6.1f} len {l:6.1f}')
    cv2.line(vis,(int(x1),int(y1)),(int(x2),int(y2)),(0,0,255),2)
cv2.imwrite('lines.png',vis)
