import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0035/scripts')
from seg import masks,S
v=sys.argv[1]
fr=np.load(f'{S}/f0035{v}.npy')
for i,f in enumerate(fr):
    green,orange=masks(f)
    m=(~green)&(~orange)
    m[680:,1020:]=False  # watermark
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,k)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    c=[(j,st[j]) for j in range(1,n) if 200<st[j][4]<6000]
    print(i,[('%.0f,%.0f'%tuple(cen[j]),s[2],s[3],s[4]) for j,s in c])
