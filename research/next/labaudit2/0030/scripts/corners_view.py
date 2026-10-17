import cv2, numpy as np
im=cv2.imread('/home/user/quantiphy-challenge/research/next/labaudit/0030/median_s.png')
print(im.shape)
C=dict(FL=(201.8,530.0),FR=(974.7,530.0),BR=(807.2,441.2),BL=(386.0,440.4))
tiles=[]
for k,(x,y) in C.items():
    x0,y0=int(x)-30,int(y)-30
    cr=im[y0:y0+60,x0:x0+60].copy()
    cr=cv2.resize(cr,None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST)
    cv2.drawMarker(cr,(int((x-x0)*6),int((y-y0)*6)),(0,255,0),cv2.MARKER_CROSS,30,1)
    cv2.putText(cr,k,(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    tiles.append(cr)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/labaudit2/0030/img/corners.png',np.hstack(tiles))
