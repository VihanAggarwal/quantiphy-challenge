import numpy as np, cv2, json
C=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0029/scripts/corners.npy')  # BL BR FR FL
f=711.0; K=np.array([[f,0,640],[0,f,360],[0,0,1.]]); Ki=np.linalg.inv(K)
sq=np.array([[0,0],[1,0],[1,1],[0,1]],float)
H,_=cv2.findHomography(sq,C)
M=Ki@H; a1,a2,a3=M[:,0],M[:,1],M[:,2]
W0=np.linalg.norm(a1); D0=np.linalg.norm(a2)
n=np.cross(a1,a2); n/=np.linalg.norm(n)
if n@a3<0: n=-n   # n points away from camera; plane n.X = h>0
import sys
mode=sys.argv[1] if len(sys.argv)>1 else 'W'
if mode=='W': s=0.760/W0
elif mode=='D': s=0.603/D0
else: s=np.sqrt(0.760/W0*0.603/D0)
h=s*(n@a3)
print('scale mode',mode,'W=%.3f D=%.3f h=%.3f'%(s*W0,s*D0,h), 'normal',n.round(3))
# corners 3D
for nm,(u,v) in zip(['BL','BR','FR','FL'],C):
    d=Ki@[u,v,1]; t=h/(n@d); X=t*d; print(nm,X.round(3),'range %.3f'%np.linalg.norm(X))
r=0.0335
trk=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0029/scripts/track_seg.json'))
P={}
for i,(u,v) in trk.items():
    d=Ki@[u,v,1]; t=(h-r)/(n@d); X=t*d; P[int(i)]=X
np.save('/home/user/quantiphy-challenge/research/next/labaudit/0029/scripts/P_plane_%s.npy'%mode, np.array([[k,*P[k]] for k in sorted(P)]))
for k in sorted(P):
    if k<19: continue
    nx=P.get(k+1)
    sp=np.linalg.norm(nx-P[k])*100 if nx is not None else np.nan
    print(k,'range %.3f'%np.linalg.norm(P[k]),'step %.2f cm'%sp)
