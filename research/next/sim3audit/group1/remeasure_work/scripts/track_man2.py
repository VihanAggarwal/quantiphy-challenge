import numpy as np, cv2, sys, json
from load import frames
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
bg=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/bg_tunnel.npy')
def track(clip):
    a=frames(D+clip+'.mp4',gray=True)
    res=[]
    for i,f in enumerate(a):
        f=f.astype(float)
        dm=((bg-f)>45).astype(np.uint8)
        dm=cv2.morphologyEx(dm,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(dm)
        k=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
        mm=lab==k
        ys,xs=np.nonzero(mm)
        top=ys.min()
        # subpixel top: in columns near head, fraction of darkness in the top row
        # dark (body, no reflection)
        dk=(f<30)&mm
        yk,xk=np.nonzero(dk)
        bot=yk.max()
        hx=xs[ys<top+15].mean()
        res.append(dict(i=i,top=int(top),bot=int(bot),hx=float(hx)))
    return a,res
if __name__=='__main__':
    for c in sys.argv[1:]:
        a,r=track(c)
        json.dump(r,open(f'../{c}_track2.json','w'))
        print(c,' '.join(f"{d['i']}:{d['top']}/{d['bot']}" for d in r))
