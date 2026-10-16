import cv2, numpy as np
fr='/home/user/quantiphy-challenge/research/next/labaudit/0029/frames/'
f=cv2.imread(fr+'rx_10.png')
g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float)
g=cv2.GaussianBlur(g,(5,5),1.5)
# front edge: along columns find strongest negative vertical gradient (bright top -> darker face) between y=520..610
for x in range(260,1120,60):
    col=g[480:640,x]
    d=np.diff(col)
    k=np.argsort(d)[:3]
    print(x,[(480+kk, round(d[kk],1), round(col[kk-2]),round(col[kk+3])) for kk in k])
