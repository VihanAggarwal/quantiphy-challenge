import numpy as np, cv2, sys, json
from load import frames
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
bg=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/bg_tunnel.npy')
def track(clip):
    a=frames(D+clip+'.mp4',gray=True)
    res=[]
    for i,f in enumerate(a):
        f=f.astype(float)
        m=((f<30)&((bg-f)>40)).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        k=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
        mm=lab==k
        ys,xs=np.nonzero(mm)
        top=ys.min(); bot=ys.max()
        # subpixel head top: column with min y; use darkness fraction of row above
        # foot analysis: lowest pixel per column in lower 15% of body
        h=bot-top
        low=mm[int(bot-0.12*h):bot+1]
        cols=np.nonzero(low.any(0))[0]
        lowest={int(c): int(int(bot-0.12*h)+np.nonzero(low[:,c])[0].max()) for c in cols}
        # head: x centre of top 5% rows
        hx=xs[ys<top+0.06*h].mean()
        # torso (pelvis approx): rows at 45-55% of height from top, mean x
        sel=(ys>top+0.45*h)&(ys<top+0.55*h)
        px=xs[sel].mean()
        res.append(dict(i=i,top=int(top),bot=int(bot),hx=float(hx),px=float(px),xmin=int(xs.min()),xmax=int(xs.max()),area=int(mm.sum()),lowest=lowest))
    json.dump(res,open(f'../{clip}_track.json','w'))
    return res
if __name__=='__main__':
    for c in sys.argv[1:]:
        r=track(c)
        for d in r[::1]:
            L=d['lowest']; cs=sorted(L)
            print(c,d['i'],d['top'],d['bot'],round(d['hx'],1),round(d['px'],1),d['xmin'],d['xmax'])
