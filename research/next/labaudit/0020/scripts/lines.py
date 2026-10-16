import cv2, numpy as np
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
ims=[cv2.imread(d+f'frames/0020_f{i:02d}.png') for i in range(0,49,4)]
med=np.median(np.stack(ims),0).astype(np.uint8)
cv2.imwrite(d+'median_o.png',med)
g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY)
g=cv2.GaussianBlur(g,(5,5),0)
e=cv2.Canny(g,15,40)
L=cv2.HoughLinesP(e,1,np.pi/360,60,minLineLength=80,maxLineGap=15)
out=med.copy()
rows=[]
for l in L.reshape(-1,4):
    x1,y1,x2,y2=[int(t) for t in l]; ang=np.degrees(np.arctan2(y2-y1,x2-x1))%180
    ln=np.hypot(x2-x1,y2-y1)
    rows.append((ln,ang,x1,y1,x2,y2))
    cv2.line(out,(x1,y1),(x2,y2),(0,0,255),2)
rows.sort(reverse=True)
for r in rows[:60]: print('len %.0f ang %.1f  (%d,%d)-(%d,%d)'%r)
cv2.imwrite(d+'lines_o.png',out)
