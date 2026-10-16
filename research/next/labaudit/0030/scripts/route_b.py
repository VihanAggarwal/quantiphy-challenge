import numpy as np, json
f=711.; c=np.array([640.,360.])
PL=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/plane.json'))
T2=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/track2.json'))
T3=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/track3.json'))
def ray(x,y): return np.array([(x-c[0])/f,(y-c[1])/f,1.])
def pos(x,y,pl,R=0.035):
    n=np.array(pl['n']); d=pl['d']
    rr=ray(x,y); t=(d+R)/(n@rr); return t*rr
stated={0.2:0.8715,0.4:1.1660,0.6:1.3720,0.8:1.3150}
for trk_name,T in [('strict-centroid',T2),('extent-centre',T3)]:
  for pname in ['W76','gm']:
    pl=PL[pname]
    for r in ['s','o']:
        P=[pos(t['cx'],t['cy'],pl) if t else None for t in T[r]]
        rng=[np.linalg.norm(p) if p is not None else np.nan for p in P]
        print(f'== {trk_name} plane={pname} render={r}')
        print(' ranges at f4,5 / 9,10 / 14,15 / 19,20:', [round(rng[i],3) for i in [4,5,9,10,14,15,19,20]])
        for tq in [0.2,0.4,0.6,0.8]:
            fr=tq*24; i0=int(np.floor(fr)); 
            # interpolated position at t, forward diff speeds
            def P_at(ff):
                a=int(np.floor(ff)); w=ff-a
                return (1-w)*P[a]+w*P[a+1]
            fw=[np.linalg.norm(P[i+1]-P[i])*24 for i in range(i0-1,i0+2)]
            cen=np.linalg.norm(P[i0+1]-P[i0])*24
            # 25fps interpretation: frame index round(t*24)
            ir=int(round(fr)); fwd_r=np.linalg.norm(P[ir+1]-P[ir])*24; ctr_r=np.linalg.norm(P[ir+1]-P[ir-1])*12
            print(f'  t={tq}: range@t={np.linalg.norm(P_at(fr)):.3f} (stated {stated[tq]}) fwd steps f{i0-1}..f{i0+1}: {[round(v,1) for v in fw]} cm? x100 ; fwd(round)={fwd_r*100:.1f} ctr(round)={ctr_r*100:.1f} cm/s')
