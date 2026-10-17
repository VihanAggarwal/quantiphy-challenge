import json, numpy as np
# Label-process emulation for family 0028 (capture clock 25 fps; video k -> capture k+(k>=12)+(k>=36))
F=711.0; CX=640.0; CY=360.0; DT=0.04
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0028/track.json'))
def cap(k): return k + (k>=12) + (k>=36)
VID={cap(k):k for k in range(49)}
THR=np.array([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95])
def mra(p,g): return ((np.abs(p-g)/g)[...,None] < 1-THR).mean(-1)
def best(L):
    grid=np.exp(np.linspace(np.log(L.min()*0.8+1e-9),np.log(np.percentile(L,99)),400))
    sc=np.array([mra(c,L).mean() for c in grid]); i=sc.argmax(); return grid[i],sc[i]
def uv(V,n):
    k=VID[n]; r=T[V][k]; return np.array([r['cx'],r['cy']])
def unit(u):
    d=np.array([(u[...,0]-CX)/F,(u[...,1]-CY)/F,np.ones(u.shape[:-1])]).T if u.ndim>1 else np.array([(u[0]-CX)/F,(u[1]-CY)/F,1.0])
    return d/np.linalg.norm(d,axis=-1,keepdims=True)
rng=np.random.default_rng(1)
N=20000; SPX=2.0; SZ=0.02
out=[]
def P(u,R): return unit(u)*R
print('=== v(1.3): forward difference at the 1.3 s frame (apex) ===')
for V in ['captured_0028x','captured_0028']:
  for n13 in (32,33):
    u1,u2=uv(V,n13),uv(V,n13+1)
    for zdot in (0.45,0.55,0.63,0.75):
        R1=1.4115; R2=R1-zdot*DT
        det=np.linalg.norm(P(u2,R2)-P(u1,R1))/DT*100
        # MC: click jitter on both frames, ToF noise: stated value = truth+e1, next = truth - zdot dt + e2
        uu1=u1+rng.normal(0,SPX,(N,2)); uu2=u2+rng.normal(0,SPX,(N,2))
        e1=rng.normal(0,SZ,N); e2=rng.normal(0,SZ,N)
        r2=R1-e1-zdot*DT+e2
        L=np.linalg.norm(unit(uu2)*r2[:,None]-unit(uu1)*R1,axis=1)/DT*100
        b,s=best(L)
        out.append((V,n13,zdot,det,np.median(L),b))
        print(f'{V[-5:]} n13={n13} (video {VID[n13]}->{VID[n13+1]}) zdot={zdot:.2f}: deterministic {det:5.1f}  MC median {np.median(L):5.1f} mean {L.mean():5.1f}  MRA-best {b:5.1f} (score {s:.3f}); score of 93.375: {mra(93.375,L).mean():.3f}, of 71.9: {mra(71.925,L).mean():.3f}, of 75: {mra(75.0,L).mean():.3f}')
