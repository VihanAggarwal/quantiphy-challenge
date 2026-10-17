# Bow/stern of the dark hull per frame in internet_0070 (rows below the shoreline), plus bimini top / hull bottom.
import cv2, numpy as np
P='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0070.mp4'
d=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/i02/boat_track.npz'); pos=d['pos']
c=cv2.VideoCapture(P); i=0; out=[]
while True:
    ok,im=c.read()
    if not ok: break
    if 28<=i<=140:
        g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        xt=int(pos[i,0]); yt=int(pos[i,1])
        x0=max(0,xt-120); x1=min(1920,xt+330)
        sub=g[yt+15:yt+60, x0:x1]   # hull band
        dark=(sub<55)
        col=dark.sum(0)
        on=col>=4
        # contiguous run around template centre (xt+95)
        cidx=xt+95-x0
        if 0<=cidx<len(on) and on[cidx]:
            l=cidx
            while l>0 and on[l-1]: l-=1
            r=cidx
            while r<len(on)-1 and on[r+1]: r+=1
            out.append((i,x0+l,x0+r,r-l+1))
        else:
            out.append((i,np.nan,np.nan,np.nan))
    i+=1
out=np.array(out,float)
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/i02/hull.npy',out)
for r in out[::4]: print(r)
