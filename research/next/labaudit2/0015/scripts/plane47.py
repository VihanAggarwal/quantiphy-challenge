# floor normal (world vertical) in camera frame from the 0047 yoga-ball centre track (round-1 cone fits, units of R)
import json, numpy as np
R=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0047/fit_x_711.json'))
X=[]
for n in range(18,43):
    r=R.get(str(n))
    if r is None: continue
    c=np.array(r['cone_c']); s=np.sin(r['alpha']); X.append(c/s)
X=np.array(X)
cen=X.mean(0); U,S,Vt=np.linalg.svd(X-cen); nrm=Vt[2]
if nrm[1]<0: nrm=-nrm   # point down (image y down)
d=nrm@cen
print('n points',len(X),'sing',S.round(3))
print('normal (down) in cam frame',nrm.round(4),'plane dist (units of R)',round(d,3))
print('pitch (deg, camera tilted down if >0):',np.degrees(np.arcsin(nrm[2])).round(2),' roll:',np.degrees(np.arctan2(-nrm[0],nrm[1])).round(2))
print('resid rms (R):',np.std((X-cen)@nrm).round(4))
for Rb in [0.2765,0.275]:
    print('R=',Rb,'camera height above floor',round((d+1)*Rb,3))
json.dump(dict(normal=nrm.tolist(),d_R=float(d)),open('../plane47.json','w'))
