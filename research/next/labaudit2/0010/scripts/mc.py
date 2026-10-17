"""Monte Carlo of the label under click jitter (sigma_px) and per-frame ToF noise (sigma_z), label frames
t=0.6 -> c15,c16,c17 ; t=0.3 -> c8,c9,c10 (half-up) or c7,c8,c9 (treal).  True track: dynamic pendulum fits
(first period) with the radial steps scaled by a route factor in [0.85,1.2] (route spread).
Label: P(c0)=stated*ray(click), P(c)=R_true_surf(c)+(eps_c-eps_c0) offset..., v=25|P1-P0|, a=625|P2-2P1+P0|.
Prints the label distribution and the expected MRA item score of candidate answers."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
sys.path.insert(0,'/home/user/quantiphy-challenge'); from qp.mra import item_scores
B='/home/user/quantiphy-challenge/research/next/labaudit2/0010/'
M=json.load(open(B+'pend3d_v2_31.json'))
rng=np.random.default_rng(1)
def score(ans,y): return np.nanmean(item_scores(np.full(len(y),ans),y))
def labels(Cc, c0, stated, spx, sz, N=20000, rf=(0.85,1.2)):
    C=np.array(Cc)[c0:c0+3]          # true centres
    Rt=np.linalg.norm(C,axis=1)-0.035 # true surface range along centre ray
    uv=np.array([[CX+F*c[0]/c[2],CY+F*c[1]/c[2]] for c in C])
    out_v=[];out_a=[];out_as=[]
    f=rng.uniform(*rf,N)
    eps=rng.normal(0,sz,(N,3)); jit=rng.normal(0,spx,(N,3,2))
    for j in range(N):
        R=stated+(Rt-Rt[0])*f[j]+eps[j]-eps[j,0]     # label ranges; stated at c0 (eps0 absorbed)
        P=np.array([R[i]*ray(*(uv[i]+jit[j,i])) for i in range(3)])
        v1=25*np.linalg.norm(P[1]-P[0]); v2=25*np.linalg.norm(P[2]-P[1])
        out_v.append(v1); out_a.append(625*np.linalg.norm(P[2]-2*P[1]+P[0])); out_as.append(abs(25*(v2-v1)))
    return np.array(out_v),np.array(out_a),np.array(out_as)
cands={'v0.6':[0.388,0.433,0.50,0.55,0.60,0.65,0.692,0.75],'a0.6':[2.83,4.0,5.0,5.5,6.0,6.5,7.0],
       'v0.3':[1.24,1.30,1.35,1.40,1.48,1.51],'a0.3':[4.89,5.02,5.5,6.0,6.5]}
model=sys.argv[1] if len(sys.argv)>1 else 'gfix+anch'
Cc=M[model]['C']
for (spx,sz) in [(1,0.005),(2,0.01),(2,0.02),(3,0.03)]:
    print(f"--- model {model} click {spx}px ToF {sz*100:.1f}cm")
    for t,c0,st in [(0.6,15,1.344),(0.3,8,1.706),(0.3,7,1.706)]:
        V,A,AS=labels(Cc,c0,st,spx,sz)
        for nm,arr in (('v',V),('a',A),('a_sp',AS)):
            key=f"{nm[0]}{t}"
            q=np.percentile(arr,[10,25,50,75,90])
            sc=' '.join(f"{a}:{score(a,arr):.3f}" for a in cands[key])
            print(f"  t={t} c{c0} {nm:4s} pct10/25/50/75/90 {np.round(q,2)} | E[score] {sc}")
