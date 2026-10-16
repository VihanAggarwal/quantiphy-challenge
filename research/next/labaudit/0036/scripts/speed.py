import numpy as np, json
f=711.; cx,cy=640.,360.
n=np.load('scripts/plane_n.npy')
T=json.load(open('scripts/trk_o.json'))
def ray(u,v):
    r=np.array([(u-cx)/f,(v-cy)/f,1.]); return r/np.linalg.norm(r)
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)
for hc in [0.154,0.157,0.160]:
    P={}
    for k in range(12,36):
        r=ray(T[str(k)]['cx'],T[str(k)]['cy']); t=hc/(n@r); P[k]=r*t
    print('hc',hc)
    s=[]
    for k in range(13,35):
        d=np.linalg.norm(P[k+1]-P[k])*100; dt=(orig(k+1)-orig(k))/25.
        s.append(d/dt)
        print('  video %d->%d orig %d  range %.3f  v=%.1f cm/s'%(k,k+1,orig(k),np.linalg.norm(P[k]),d/dt))
