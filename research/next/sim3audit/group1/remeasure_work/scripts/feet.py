import numpy as np, cv2, sys, json
from load import frames
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
bg=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/bg_tunnel.npy')
clip=sys.argv[1]
a=frames(D+clip+'.mp4',gray=True)
tr=json.load(open(f'../{clip}_track2.json'))
out=[]
for i,f in enumerate(a):
    f=f.astype(float)
    top=tr[i]['top']; bot=tr[i]['bot']; h=bot-top
    y0=int(bot-0.22*h)
    dk=((f<30)&((bg-f)>40)).astype(np.uint8)
    sub=dk[y0:bot+3]
    sub=cv2.morphologyEx(sub,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(sub)
    comps=[]
    for k in range(1,n):
        if st[k,cv2.CC_STAT_AREA]<40: continue
        ys,xs=np.nonzero(lab==k)
        yb=ys.max()
        xb=xs[ys>=yb-2].mean()
        comps.append((float(xb),int(yb+y0),int(st[k,cv2.CC_STAT_AREA])))
    comps.sort()
    out.append(comps)
    print(i, top, bot, [(round(c[0]),c[1]) for c in comps])
json.dump(out,open(f'../{clip}_feet.json','w'))
