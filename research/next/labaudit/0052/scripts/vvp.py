import cv2, numpy as np
f = cv2.imread('frames/o_00.png')
g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
e = cv2.Canny(cv2.GaussianBlur(g,(3,3),0), 30, 90)
L = cv2.HoughLinesP(e, 1, np.pi/720, 80, minLineLength=120, maxLineGap=6)
ls=[]
for x1,y1,x2,y2 in L.reshape(-1,4):
    ang = np.degrees(np.arctan2(x2-x1, y2-y1))
    if abs(ang) < 8 or abs(abs(ang)-180)<8:
        ls.append((x1,y1,x2,y2,np.hypot(x2-x1,y2-y1)))
ls=np.array(ls)
for l in ls[np.argsort(ls[:,0])]: print(np.round(l,1))
np.save('vlines.npy', ls)
vis=f.copy()
for x1,y1,x2,y2,_ in ls.astype(int): cv2.line(vis,(x1,y1),(x2,y2),(0,0,255),2)
cv2.imwrite('vlines.png',vis)
