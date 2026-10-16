import cv2, numpy as np
med=cv2.imread('median_o.png')
g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY)
e=cv2.Canny(cv2.GaussianBlur(g,(5,5),0),15,45)
L=cv2.HoughLinesP(e,1,np.pi/720,50,minLineLength=60,maxLineGap=8)
ls=[]
for x1,y1,x2,y2 in L.reshape(-1,4):
    if y1>y2: x1,y1,x2,y2=x2,y2,x1,y1
    ang=np.degrees(np.arctan2(x2-x1,y2-y1))  # 0=vertical down
    ls.append((x1,y1,x2,y2,np.hypot(x2-x1,y2-y1),ang))
ls=np.array(ls)
sel=ls[(np.abs(ls[:,5])<40)]
for l in sel[np.argsort(sel[:,0])]: print(np.round(l,1))
vis=med.copy()
for x1,y1,x2,y2,_,_ in sel.astype(int): cv2.line(vis,(x1,y1),(x2,y2),(0,0,255),2)
cv2.imwrite('vlines2.png',vis)
