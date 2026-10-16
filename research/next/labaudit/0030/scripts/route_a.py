import numpy as np, json
f=711.; c=np.array([640.,360.])
PL=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/plane.json'))
T2=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/track2.json'))
T3=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/track3.json'))
tA=np.array([0.2,0.4,0.6,0.8]); rA=np.array([0.8715,1.1660,1.3720,1.3150])
def u(x,y):
    v=np.array([(x-c[0])/f,(y-c[1])/f,1.]); return v/np.linalg.norm(v)
def pos_plane(x,y,pl,R=0.035):
    n=np.array(pl['n']); d=pl['d']; rr=np.array([(x-c[0])/f,(y-c[1])/f,1.]); return (d+R)/(n@rr)*rr
res={}
for trk_name,T in [('strict',T2),('extent',T3)]:
  for r in ['s','o']:
    tr=T[r]
    pp=[pos_plane(t['cx'],t['cy'],PL['gm']) for t in tr[:24]]
    rng_plane=np.array([np.linalg.norm(p) for p in pp])
    # depth model 1: linear interpolation of stated anchors (extrapolate linearly at ends)
    tt=np.arange(24)/24
    rng1=np.interp(tt,tA,rA)
    # extrapolate before 0.2 with first segment slope
    s0=(rA[1]-rA[0])/0.2; rng1=np.where(tt<0.2, rA[0]+s0*(tt-0.2), rng1)
    s3=(rA[3]-rA[2])/0.2; rng1=np.where(tt>0.8, rA[3]+s3*(tt-0.8), rng1)
    # depth model 2: plane ranges rescaled piecewise to the anchors (ratio interpolated)
    rp_at=np.interp(tA*24,np.arange(24),rng_plane)
    ratio=np.interp(tt,tA,rA/rp_at)
    rng2=rng_plane*ratio
    # depth model 3: plane ranges with a single global factor (median ratio)
    rng3=rng_plane*np.median(rA/rp_at)
    out={}
    for mname,rng in [('anchorlin',rng1),('plane-anch',rng2),('plane-glob',rng3)]:
        P=np.array([rng[i]*u(tr[i]['cx'],tr[i]['cy']) for i in range(24)])
        sp=np.linalg.norm(np.diff(P,axis=0),axis=1)*24*100
        row=[]
        for tq in [0.2,0.4,0.6,0.8]:
            fr=tq*24; i=int(round(fr)); a=int(np.floor(fr))
            fwd=sp[i]          # P[i+1]-P[i]
            fwd_floor=sp[a]
            ctr=np.linalg.norm(P[i+1]-P[i-1])*12*100
            row.append((round(fwd_floor,1),round(fwd,1),round(ctr,1)))
        out[mname]=row
        print(f'{trk_name:7s} {r} {mname:11s}', '  '.join(f't={tq}: floor/round/ctr={v}' for tq,v in zip([0.2,0.4,0.6,0.8],row)))
    res[f'{trk_name}_{r}']=out
    print('   plane/stated ratio at anchors', np.round(rA/rp_at,3))
json.dump(res,open('/home/user/quantiphy-challenge/research/next/labaudit/0030/route_a.json','w'))
