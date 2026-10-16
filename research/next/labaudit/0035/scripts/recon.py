import numpy as np, json, sys
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
F=711.0; CX=640.0; CY=360.0
def ray(u,v):
    d=np.array([(u-CX)/F,(v-CY)/F,1.0]); return d/np.linalg.norm(d)
def load(v):
    r=json.load(open(f'{S}/tr_{v}.json'))
    return {k:{int(i):d for i,d in r[k].items()} for k in r}
def size_track(tr,D,szkey='minor'):
    P={}
    for i,d in tr.items():
        rng=F*D/d[szkey]   # range ~ f*D/d (surface-click convention calibrated below)
        P[i]=rng*ray(d['cx'],d['cy'])
    return P
def fit_plane(pts):
    pts=np.array(pts); c=pts.mean(0); u,s,vt=np.linalg.svd(pts-c); n=vt[2]
    if n[1]>0: n=-n   # normal pointing up (image y down => up is -y)
    return n,c, s
def plane_track(tr,n,c,offset=0.0):
    # plane: n.(X-c)=offset
    P={}
    for i,d in tr.items():
        r=ray(d['cx'],d['cy']); t=(offset+n@c)/(n@r); P[i]=t*r
    return P
