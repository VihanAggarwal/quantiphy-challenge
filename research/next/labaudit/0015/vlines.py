import cv2, numpy as np
R='/home/user/quantiphy-challenge/data/QuantiPhy/'
c=cv2.VideoCapture(R+'captured_0041.mp4'); ok,f=c.read()
g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
e=cv2.Canny(cv2.GaussianBlur(g,(3,3),0),8,25)
L=cv2.HoughLinesP(e,1,np.pi/720,40,minLineLength=90,maxLineGap=15)
vis=f.copy(); segs=[]
for l in L.reshape(-1,4):
    x1,y1,x2,y2=l
    if abs(x2-x1)<0.15*abs(y2-y1):
        segs.append(l); cv2.line(vis,(x1,y1),(x2,y2),(0,0,255),2)
        print(l, 'dx/dy=%.4f'%((x2-x1)/(y2-y1)), 'xmid', (x1+x2)/2)
cv2.imwrite('xref/vlines41.jpg',vis,[cv2.IMWRITE_JPEG_QUALITY,85])
