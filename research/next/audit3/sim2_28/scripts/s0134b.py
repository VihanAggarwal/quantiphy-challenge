import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('simulation_0134')
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in F]
# toast bbox at frame 43 by diff vs frame 59 (toast back down) in region above toaster top
d=np.abs(G[43]-G[0]); d=cv2.GaussianBlur(d,(5,5),0)
sub=d[800:1130, 300:800]
m=sub>25
ys,xs=np.where(m)
print('toast region f43 y',ys.min()+800,ys.max()+800,'x',xs.min()+300,xs.max()+300)
# template track: toast template from frame 43 (fully visible)
y0,y1=ys.min()+800+5, ys.min()+800+120
x0,x1=xs.min()+300+5, xs.max()+300-5
T=G[43][y0:y1,x0:x1]
for i in range(36,60):
    r=cv2.matchTemplate(G[i][600:1300, x0-30:x1+30],T,cv2.TM_CCOEFF_NORMED)
    _,mx,_,loc=cv2.minMaxLoc(r)
    # subpixel parabola in y
    yy=loc[1]; xx=loc[0]
    if 0<yy<r.shape[0]-1:
        a,b,c=r[yy-1,xx],r[yy,xx],r[yy+1,xx]; off=0.5*(a-c)/(a-2*b+c)
    else: off=0
    print(i, round(600+yy+off-y0,2), round(mx,3))
