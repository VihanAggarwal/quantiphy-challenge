# curated centroids (video frame index at 24 fps); from SAM-segmented renders ax (camera a) and bx (camera b)
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from geom import *
def track(v,frames,seeds,colfun,maxd=80):
    out={}
    for i in frames:
        cs=comps(v,i)
        cs=[c for c in cs if colfun(c['bgr']) and 150<c['A']<3000]
        if not cs: continue
        c=min(cs,key=lambda c: np.hypot(*(c['c']-np.array(seeds[i]))) )
        if np.hypot(*(c['c']-np.array(seeds[i])))<maxd: out[i]=(c['c'],c['A'],c['bbox'],c['mask'])
    return out
