import cv2, numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work')
from recon import *
f=4240.
K,Ki,D,L,U=cam(f)
H=json.load(open(W+'hubs.json'))
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0311.mp4')
fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im)
outs=[]
for nm in ['RW','FW']:
    Q,_=tri({int(k):v for k,v in H[nm].items()},f)
    for k in [30,48]:
        img=fr[k].copy()
        P0=Q+(k-24)/24*D
        cols=[(0,255,255),(0,255,0),(255,0,0),(255,0,255),(0,0,255)]
        for j,rho in enumerate([0.045,0.050,0.055,0.060,0.065]):
            pts=[]
            for th in np.linspace(0,2*np.pi,200):
                P=P0+rho*(np.cos(th)*D+np.sin(th)*U); p=K@P; pts.append(p[:2]/p[2])
            pts=np.int32(np.array(pts)*4)
            cv2.polylines(img,[pts.reshape(-1,1,2)],True,cols[j],1,lineType=cv2.LINE_AA,shift=2)
        p=K@P0; p=p[:2]/p[2]; x,y=int(p[0]),int(p[1])
        s=110 if k==30 else 80
        crop=cv2.resize(img[y-s:y+s,x-s:x+s],(400,400),interpolation=cv2.INTER_CUBIC)
        outs.append(crop)
cv2.imwrite(W+'wheelcircles.png',np.vstack([np.hstack(outs[:2]),np.hstack(outs[2:])]))
