import cv2, numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work')
from recon import *
f=float(sys.argv[1]) if len(sys.argv)>1 else 4240.
K,Ki,D,L,U=cam(f)
TL=json.load(open(W+'taillights.json'))
QL,_=tri({int(k):v for k,v in TL['TLL'].items() if int(k)>=22},f)
QR,_=tri({int(k):v for k,v in TL['TLR'].items() if int(k)>=31},f)
O=(QL+QR)/2
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0311.mp4')
fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im)
def proj(P):
    p=K@P; return p[:2]/p[2]
# box corners of roof search region
box=[O+a*D+b*L+cc*U for a in (0.15,0.45) for b in (-0.12,0.12) for cc in (0.0,0.10)]
res={}
phis=None
frames=list(range(28,68,1))
for k in frames:
    pts=np.array([proj(P+(k-24)/24*D) for P in box])
    hull=cv2.convexHull(np.float32(pts))
    im=fr[k].astype(np.float32)
    red=cv2.GaussianBlur(im[...,2]-np.maximum(im[...,1],im[...,0]),(5,5),0)
    ang=np.degrees(np.arctan2(pts[:,1]-vD[1],pts[:,0]-vD[0]))
    if phis is None:
        phis=np.linspace(ang.min(),ang.max(),80)
    for ph in phis:
        u=np.array([np.cos(np.radians(ph)),np.sin(np.radians(ph))])
        dist=np.linspace(np.linalg.norm(pts-vD,axis=1).min()-5,np.linalg.norm(pts-vD,axis=1).max()+5,800)
        P=vD+dist[:,None]*u
        inside=np.array([cv2.pointPolygonTest(hull,(float(x),float(y)),False)>=0 for x,y in P])
        if inside.sum()<20: continue
        vals=cv2.remap(red,np.float32(P[:,0]).reshape(1,-1),np.float32(P[:,1]).reshape(1,-1),cv2.INTER_LINEAR).ravel()
        # walk from far (large dist, rear) toward vD: find first index (from far side) where we are in dark (<15) then become red (>45) closer to vD
        idx=np.where(inside)[0]
        v=vals[idx]; dd=dist[idx]
        # order from far to near vD
        o=np.argsort(-dd); v=v[o]; dd=dd[o]
        dark=False; hit=None
        for j in range(len(v)):
            if v[j]<15: dark=True; jd=j
            elif dark and v[j]>45:
                # refine crossing at 30
                jj=j
                while jj>0 and v[jj-1]>30: jj-=1
                hit=dd[jj]; break
        if hit is not None:
            res.setdefault(round(float(ph),4),{})[k]=list(map(float,vD+hit*u))
out=[]
for ph,tr in res.items():
    if len(tr)<15: continue
    trk={int(k):v for k,v in tr.items()}
    Q,r=tri(trk,f)
    d=Q-O
    out.append((ph,len(tr),r,d@D,d@L,d@U))
out=np.array(out)
np.save(W+'roof_f%d.npy'%f,out)
for row in out: print(np.round(row,4))
