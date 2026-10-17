# Capsule geometry of the ball blob: PCA axes, length and width (perpendicular extent), per frame.
import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0033/scripts')
from geo import *
R=sys.argv[1] if len(sys.argv)>1 else 'x'
p='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0033%s.mp4'%('' if R=='o' else R)
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
fr=np.array(fr); med=np.median(fr,axis=0).astype(np.int16)
T=load_track(R); out={}
for k in sorted(T):
    e=T[k]
    d=np.abs(fr[k].astype(np.int16)-med).max(axis=2)
    m=(d>35).astype(np.uint8); m[685:,1000:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # pick component containing the tracked centroid neighbourhood
    kk=np.argmin([np.hypot(cen[j,0]-e['cx'],cen[j,1]-e['cy']) if j>0 else 1e9 for j in range(n)])
    ys,xs=np.nonzero(lab==kk)
    P=np.c_[xs,ys].astype(float); mu=P.mean(0); C=np.cov((P-mu).T)
    w,V=np.linalg.eigh(C); a1=V[:,1]; a2=V[:,0]
    p1=(P-mu)@a1; p2=(P-mu)@a2
    L=np.percentile(p1,99.5)-np.percentile(p1,0.5); W=np.percentile(p2,99.5)-np.percentile(p2,0.5)
    # width as max chord perpendicular: area/(L-W)+... capsule area = W*(L-W)+pi W^2/4
    A=len(xs); # solve capsule: A = W*(L-W) + pi*W^2/4 for W given L
    # quadratic: (pi/4-1) W^2 + L W - A = 0
    a=(np.pi/4-1); Wc=(-L+np.sqrt(L*L+4*a*A))/(2*a)
    ang=np.degrees(np.arctan2(a1[1],a1[0]))
    out[k]=dict(L=float(L),W=float(W),Wc=float(Wc),ang=float(ang),mu=mu.tolist(),bottom=int(ys.max()),top=int(ys.min()))
    print(k,'c%d'%cap(k),'mu(%.1f,%.1f) L %.1f W %.1f Wcaps %.1f ang %.0f top %d bot %d'%(mu[0],mu[1],L,W,Wc,ang,ys.min(),ys.max()))
json.dump(out,open(BASE+'streak_%s.json'%R,'w'),indent=0)
