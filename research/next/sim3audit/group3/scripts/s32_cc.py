import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0032_segmented.mp4')
i=0
while True:
    ok,f=c.read()
    if not ok: break
    g=f.astype(int)
    m=((255*3-g.sum(2))>60).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=[(st[k,0],st[k,1],st[k,2],st[k,3],st[k,4]) for k in range(1,n) if st[k,4]>30]
    if i%5==0 or len(comps)>2: print(i, comps)
    i+=1
