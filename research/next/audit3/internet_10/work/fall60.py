import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0060.mp4')
F={};k=0
while True:
    ok,f=c.read()
    if not ok: break
    if 44<=k<=68 or 76<=k<=100: F[k]=f.astype(np.int16)
    k+=1
bg=np.median(np.stack([F[k] for k in range(80,100,2)]),axis=0)
for k in range(44,68):
    d=np.abs(F[k]-bg).max(axis=2)
    d[:, 1300:]=0; d[:350]=0; d[850:]=0
    m=(d>28).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(k,'none'); continue
    # take components right of x=150 (exclude hand) largest
    cand=[j for j in range(1,n) if st[j,4]>400]
    s=' '.join('[x%d-%d y%d-%d a%d c%.0f]'%(st[j,0],st[j,0]+st[j,2],st[j,1],st[j,1]+st[j,3],st[j,4],cen[j][0]) for j in sorted(cand,key=lambda j:st[j,0]))
    print(k,s)
