import cv2, numpy as np
from common import load
fr=load('x')
for i in [0,4,8,30,40,70]:
    f=fr[i]; nw=(f.astype(int).min(axis=2)<215); nw[650:,1000:]=False
    n,lab,st,cen=cv2.connectedComponentsWithStats(nw.astype(np.uint8))
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    m=(lab==k)
    # widest grey-shirt extent in shoulder band (rows y+75..y+110)
    ws=[]
    for r in range(y+70,y+115,5):
        xs=np.nonzero(m[r])[0]; ws.append((r,xs.min(),xs.max(),xs.max()-xs.min()))
    print(i,'person bbox top',y,'bottom',y+h,'height px',h, ' shoulder rows', [(r,a,b,wd) for r,a,b,wd in ws[::2]])
