import sys, cv2, numpy as np, json; sys.path.insert(0,'scripts')
from models import M
def binmask(n):
    im=cv2.imread(f'frames/x_{n:02d}.png').astype(int)
    m=(~((im[...,1]>200)&(im[...,2]<80)&(im[...,0]<80))).astype(np.uint8)
    m[690:,1000:]=0
    k,lab,st,cen=cv2.connectedComponentsWithStats(m)
    cand=[i for i in range(1,k) if st[i][4]>4000 and not (abs(cen[i][0]-986)<6 and abs(cen[i][1]-370)<6)]
    i=max(cand,key=lambda i:st[i][4]); return (lab==i).astype(np.uint8)
for n in (10,22,34,40,47):
    m=binmask(n)
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)
    hull=cv2.convexHull(c)
    for e in np.arange(1,20,0.5):
        ap=cv2.approxPolyDP(hull,e,True)
        if len(ap)<=6: break
    poly=ap.reshape(-1,2)
    print('n',n,'hexagon',poly.tolist())
