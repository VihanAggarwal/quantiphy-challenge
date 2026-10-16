import cv2, numpy as np
fr=[cv2.imread(f'frames/o_{n:02d}.png').astype(float) for n in range(0,48,3)]
med=np.median(np.stack(fr),0).astype(np.uint8)
cv2.imwrite('median_o.png',med)
g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY)
e=cv2.Canny(cv2.GaussianBlur(g,(3,3),0),30,90)
L=cv2.HoughLinesP(e,1,np.pi/720,60,minLineLength=80,maxLineGap=6)
ls=[]
for x1,y1,x2,y2 in L.reshape(-1,4):
    ang=np.degrees(np.arctan2(x2-x1,y2-y1))
    if abs(ang)<25 or abs(abs(ang)-180)<25:
        ls.append((x1,y1,x2,y2,np.hypot(x2-x1,y2-y1),ang))
ls=np.array(ls)
for l in ls[np.argsort(ls[:,0])]: print(np.round(l,1))
vis=med.copy()
for x1,y1,x2,y2,_,_ in ls.astype(int): cv2.line(vis,(x1,y1),(x2,y2),(0,0,255),2)
cv2.imwrite('vlines.png',vis)
np.save('vlines.npy',ls)
