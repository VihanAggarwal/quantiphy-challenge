import cv2, numpy as np
from extract import load
fr=load('x')
for i in range(0,73,3):
    f=fr[i].astype(int)
    nonwhite=(f.min(axis=2)<200)
    nonwhite[650:,1000:]=False  # watermark
    ys,xs=np.nonzero(nonwhite)
    n,lab,st,cen=cv2.connectedComponentsWithStats(nonwhite.astype(np.uint8))
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    print(i,'main comp bbox x',x,x+w,'y',y,y+h,'area',a, 'ncomp>200:',[tuple(s) for s in st[1:] if s[4]>200 and not (s[0]==x and s[1]==y)])
