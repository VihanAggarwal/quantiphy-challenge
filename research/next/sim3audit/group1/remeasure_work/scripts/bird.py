import numpy as np, cv2, json
from load import frames
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
for clip in ['simulation_0010_segmented','simulation_0010']:
    a=frames(D+clip+'.mp4',gray=True).astype(np.int16)
    bg=np.median(a,axis=0)
    res=[]
    for i,f in enumerate(a):
        m=(np.abs(f-bg)>40).astype(np.uint8)
        m[1400:]=0
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: res.append(None); continue
        k=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
        # dark bird pixels: restrict to dark
        ys,xs=np.nonzero(lab==k)
        res.append(dict(i=i,cx=float(xs.mean()),cy=float(ys.mean()),x0=int(xs.min()),x1=int(xs.max()),y0=int(ys.min()),y1=int(ys.max()),area=int(len(xs))))
    json.dump(res,open(f'../{clip}_bird.json','w'))
    print(clip)
    for r in res: print(r)
