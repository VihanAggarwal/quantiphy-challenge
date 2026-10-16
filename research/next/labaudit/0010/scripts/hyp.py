import numpy as np, json
rows=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0010/track_s.json'))
f=711.0; c=(640.0,360.0)
fr=np.arange(49); u=np.array([r['u'] for r in rows]); v=np.array([r['v'] for r in rows]); Dx=np.array([r['Dx'] for r in rows])
gd={0.3:1.7060,0.6:1.3440,0.9:1.4605,1.2:1.7840,1.5:1.7170,1.8:1.3500}
def bp(uu,vv,rng):
    d=np.array([(uu-c[0])/f,(vv-c[1])/f,1.0]); return d/np.linalg.norm(d)*rng
for fps in [24.0]:
    P={t:bp(np.interp(t*fps,fr,u),np.interp(t*fps,fr,v),r) for t,r in gd.items()}
    ts=sorted(P)
    print('Chord velocities with given ranges (0.3 s steps):')
    V={}
    for a,b in zip(ts[:-1],ts[1:]):
        V[a]=(P[b]-P[a])/(b-a); print(f'  v({a})={np.linalg.norm(V[a]):.3f}  vec={np.round(V[a],3)}')
    print('Second differences:')
    for a in ts[1:-1]:
        acc=(P[round(a+0.3,1)]-2*P[a]+P[round(a-0.3,1)])/0.09
        print(f'  central a({a})={np.linalg.norm(acc):.3f}')
    for a in ts[:-2]:
        acc=(V[round(a+0.3,1)]-V[a])/0.3
        print(f'  forward a({a})={np.linalg.norm(acc):.3f}')
# image displacement only (2D) at 1 frame
for t in [0.3,0.6]:
    i=t*24
    print(f't={t} image speed px/frame {np.hypot(np.interp(i+1,fr,u)-np.interp(i,fr,u),np.interp(i+1,fr,v)-np.interp(i,fr,v)):.2f}')
