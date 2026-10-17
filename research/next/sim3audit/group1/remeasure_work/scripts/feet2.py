import numpy as np, cv2, sys, json
from load import frames
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
bg=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/bg_tunnel.npy')
clip=sys.argv[1]; thr=float(sys.argv[2]) if len(sys.argv)>2 else 6
a=frames(D+clip+'.mp4',gray=True)
tr=json.load(open(f'../{clip}_track2.json'))
out=[]
for i,f in enumerate(a):
    f=f.astype(float)
    top=tr[i]['top']; bot=tr[i]['bot']; h=bot-top
    y0=int(bot-0.25*h)
    dk=((f<thr)&((bg-f)>40)).astype(np.uint8)
    sub=dk[y0:bot+5]
    sub=cv2.morphologyEx(sub,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(sub)
    comps=[]
    for k in range(1,n):
        if st[k,cv2.CC_STAT_AREA]<60: continue
        ys,xs=np.nonzero(lab==k)
        yb=ys.max()
        # bottom row extent: pixels within 3 px of bottom
        sel=ys>=yb-3
        comps.append((float(xs[sel].mean()),int(yb+y0),int(xs[sel].min()),int(xs[sel].max())))
    comps.sort()
    out.append(comps)
    print(i, tr[i]['top'], [(round(c[0]),c[1],c[2],c[3]) for c in comps])
json.dump(out,open(f'../{clip}_feet2.json','w'))
