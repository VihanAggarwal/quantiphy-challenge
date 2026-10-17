import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=[f.astype(np.float32) for f in frames('simulation_0090')]
bg=np.median(np.stack(F[20:30]),axis=0)
# route 2: luminance darkness profile; small bird column extent via column-sum of |diff| with half-max of column profile tails
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in F]
gb=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY)
res=[]
for i in range(3,19):
    d=np.clip(gb-G[i],0,None)  # bird darker than sky
    # restrict to small bird region: x from bbox estimate
    sub=d[500:700]
    m=sub>20
    cols=np.where(m.any(axis=0))[0]
    # split clusters
    gaps=np.where(np.diff(cols)>20)[0]
    groups=np.split(cols,gaps+1)
    g=[gg for gg in groups if len(gg)>30]
    # small bird is rightmost group while eagle present; for i>=12 only one
    sb=g[-1]
    res.append((i,sb[0],sb[-1],sb[-1]-sb[0]+1))
for r in res: print(r)
L=np.array([r[3] for r in res]); print('median extent',np.median(L))
# speed by template cross-correlation of small bird between frames 4->16 (same flap phase? period ~9)
x0=np.array([r[1] for r in res]); x1=np.array([r[2] for r in res])
fr=np.array([r[0] for r in res])
print('left edge slope',np.polyfit(fr,x0,1)[0],'right edge slope',np.polyfit(fr,x1,1)[0])
# phase-correlation template matching
def track(i,j,box):
    y0,y1,xa,xb=box
    T=G[i][y0:y1,xa:xb]
    r=cv2.matchTemplate(G[j],T,cv2.TM_CCOEFF_NORMED)
    _,mx,_,loc=cv2.minMaxLoc(r)
    return loc[0]-xa, loc[1]-y0, mx
for i,j in [(4,13),(5,14),(3,12),(6,15),(7,16)]:
    # small bird box at frame i from res
    rr=[r for r in res if r[0]==i][0]
    dx,dy,mx=track(i,j,(570,650,rr[1]-5,rr[2]+5))
    print(i,j,dx/(j-i),dy,mx)
print('eagle')
for i,j in [(2,6),(3,7),(2,10),(3,9)]:
    # eagle box: from first script eagle left edge 1392-156*(i-2)
    xa=int(1392-156.3*(i-2))-5; xb=xa+192
    dx,dy,mx=track(i,j,(420,700,xa,xb))
    print(i,j,dx/(j-i),dy,mx)
# distance at frame 7 by centroid-of-darkness per bird
for i in [7,8]:
    d=np.clip(gb-G[i],0,None); d[d<15]=0
    sub=d[450:800]
    cols=sub.sum(axis=0)
    xs=np.arange(len(cols))
    e=(xs<1000); s=(xs>=1000)
    ce=(cols*xs*e).sum()/(cols*e).sum(); cs=(cols*xs*s).sum()/(cols*s).sum()
    print(i,'centroid sep',cs-ce,'m',(cs-ce)*0.004791)
