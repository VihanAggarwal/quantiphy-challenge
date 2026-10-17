import numpy as np, cv2, json
from load import frames
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
clip='simulation_0010_segmented'
a=frames(D+clip+'.mp4')
tr=json.load(open(f'../{clip}_bird.json'))
out=[]
prev=None
for i,f in enumerate(a):
    cx=int(tr[i]['cx']); cy=int(tr[i]['cy'])
    x0=max(cx-160,0); y0=cy-110
    c=f[y0:cy+110, x0:cx+160]
    hsv=cv2.cvtColor(c,cv2.COLOR_BGR2HSV)
    dark=(hsv[...,2]<60).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(dark)
    if n<2: out.append(None); continue
    k=1+np.argmax(st[1:,4])
    ys,xs=np.nonzero(lab==k)
    # dark body: rightmost point at the head row region, leftmost
    out.append(dict(i=i,dx0=int(xs.min()+x0),dx1=int(xs.max()+x0),dcx=float(xs.mean()+x0),dcy=float(ys.mean()+y0),area=len(xs)))
for o in out: print(o)
json.dump(out,open(f'../{clip}_dark.json','w'))
