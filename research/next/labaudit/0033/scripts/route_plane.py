import numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0033/scripts')
from plane import table_plane, ray
tr=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0033/track_x_raw.json'))
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)
for mode in ['W','avg','D']:
    X,n,h=table_plane(mode=mode)
    pos={}
    for k in range(24,37):
        u,v=tr[k][0]['cx'],tr[k][0]['cy']
        d=ray(u,v)
        # plane offset by R=2: n.x + h - 2 = 0 -> lam = (2-h)/(n.d)
        lam=(2.0-h)/np.dot(n,d); p=lam*d; pos[k]=p
    print(mode,'h=%.1f'%h)
    ks=sorted(pos)
    for a,b in zip(ks[:-1],ks[1:]):
        dt=(orig(b)-orig(a))/25.
        v=np.linalg.norm(pos[b]-pos[a])/dt
        print('  video %d->%d orig %d->%d  range_a=%.1f  v=%.1f cm/s  comps %s'%(a,b,orig(a),orig(b),np.linalg.norm(pos[a]),v,np.round((pos[b]-pos[a])/dt,1)))
