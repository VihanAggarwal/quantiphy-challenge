import cv2, numpy as np
a=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0229.mp4')
b=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0230.mp4')
i=0; rows=[]
while True:
    oka,fa=a.read(); okb,fb=b.read()
    if not (oka and okb): break
    d=np.sqrt(((fa.astype(np.float32)-fb.astype(np.float32))**2).sum(axis=2))
    d=cv2.GaussianBlur(d,(5,5),0)
    m=(d>18).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); i+=1; continue
    order=np.argsort(-st[1:,4])[:3]+1
    print(i, [(tuple(int(v) for v in st[k][:5])) for k in order])
    if i in (0,24,49):
        cv2.imwrite(f'catdiff_{i:02d}.png', cv2.resize(np.clip(d*4,0,255).astype(np.uint8),None,fx=0.5,fy=0.5))
    i+=1
