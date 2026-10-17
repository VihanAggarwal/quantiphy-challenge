import sys, os, math, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import ballfit as B
def fd(r,c): 
    P=B.model(r['q'],np.array([c/25,(c+1)/25]),r['th'],r['rho'],r['g'])
    return np.linalg.norm(P[1]-P[0])*25
print('Route 2: gravity-only scale (no ToF anchor)')
for lab,kw in [('pitch/roll free',{}),('pitch 1.0',dict(th=math.radians(1),rho=0.0)),('pitch 2.5 roll -0.6',dict(th=math.radians(2.5),rho=math.radians(-0.6))),('tennis-fit pitch',dict(th=math.radians(-0.1),rho=math.radians(-1.1)))]:
    for c0 in (24,26):
        r=B.fit('white',c0,39,**kw)
        P25=B.model(r['q'],np.array([1.0]),r['th'],r['rho'],r['g'])[0]
        print(' %-22s c%d-39 rms=%.2f range@c25=%.3f (ToF surface 3.0735 -> centre 3.107) c37->38=%.3f c38->39=%.3f'%(lab,c0,r['rms'],np.linalg.norm(P25),fd(r,37),fd(r,38)))
# timing check: no second drop (video k -> capture k+1 for k>=12)
orig=B.cap
B.cap=lambda k: k + (1 if k>=12 else 0)
r=B.fit('white',24,38,anchor=3.0735+0.033)
print('timing check without the 35->36 drop: rms=%.2f px (with drop: ~0.7 px)'%r['rms'])
B.cap=lambda k: k
r=B.fit('white',23,37,anchor=3.0735+0.033)
print('timing check, pure 24 fps video clock (t=k/24 relabelled as c): rms=%.2f px'%r['rms'])
