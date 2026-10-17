"""Expected MRA item score of current vs proposed answers for v(0.6) and a(0.6) under the label-noise MC
(mc.labels), true track = pendulum fit 'a07' (pend3d_v3.json), radial steps scaled by f in rf.
Also the smooth-label case (no noise) and the 0.3 s chord hypothesis for reference."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
import importlib, numpy as np
sys.argv=['mc']; mc=importlib.import_module('mc') if False else None
from common import *
sys.path.insert(0,'/home/user/quantiphy-challenge'); from qp.mra import item_scores
B='/home/user/quantiphy-challenge/research/next/labaudit2/0010/'
Cc=json.load(open(B+'pend3d_v3.json'))['a07']['C']
rng=np.random.default_rng(7)
def labels(c0,stated,spx,sz,rf,N=20000):
    C=np.array(Cc)[c0:c0+3]; Rt=np.linalg.norm(C,axis=1)-0.035
    uv=np.array([[CX+F*c[0]/c[2],CY+F*c[1]/c[2]] for c in C])
    f=rng.uniform(*rf,N); eps=rng.normal(0,sz,(N,3)); jit=rng.normal(0,spx,(N,3,2))
    V=np.empty(N); A=np.empty(N)
    for j in range(N):
        R=stated+(Rt-Rt[0])*f[j]+eps[j]-eps[j,0]
        P=np.array([R[i]*ray(*(uv[i]+jit[j,i])) for i in range(3)])
        V[j]=25*np.linalg.norm(P[1]-P[0]); A[j]=625*np.linalg.norm(P[2]-2*P[1]+P[0])
    return V,A
sc=lambda a,y: float(np.mean(item_scores(np.full(len(y),a),y)))
print("scenario                         | v(0.6): 0.388  0.433  0.692 | a(0.6): 2.83  2.90  6.8")
for rf in ((0.85,1.2),(1.0,1.2)):
    for spx,sz in ((0,0.0),(1,0.005),(2,0.01),(2,0.02),(3,0.03)):
        V,A=labels(15,1.344,spx,sz,rf if spx else (1.0,1.0001))
        print(f"rf{rf} click {spx}px ToF {sz*100:.1f}cm | {sc(0.388,V):.3f} {sc(0.433,V):.3f} {sc(0.692,V):.3f} | {sc(2.83,A):.3f} {sc(2.90,A):.3f} {sc(6.8,A):.3f}   (median label v {np.median(V):.3f}, a {np.median(A):.2f})")
ch_v=np.array([0.39]); ch_a=np.array([3.07])
print(f"0.3 s chord hypothesis (v 0.39, a 3.07)  | {sc(0.388,ch_v):.3f} {sc(0.433,ch_v):.3f} {sc(0.692,ch_v):.3f} | {sc(2.83,ch_a):.3f} {sc(2.90,ch_a):.3f} {sc(6.8,ch_a):.3f}")
