"""Emulate the pipeline that produced the current answers: clicked centre back-projected with the range
linearly interpolated between the stated 0.3 s anchors (anchor times on the 24 fps video clock or the 25 fps
capture clock), forward differences over one frame."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
B='/home/user/quantiphy-challenge/research/next/labaudit2/0010/'
T=json.load(open(B+'track.json'))
k=np.arange(49); n=np.array([cap(i) for i in k])
u=np.array([T['s'][i]['u'] for i in k]); v=np.array([T['s'][i]['v'] for i in k])
ts=np.array([0.3,0.6,0.9,1.2,1.5,1.8]); Rs=np.array([1.706,1.344,1.4605,1.784,1.717,1.350])
def interp(t): return np.interp(t,ts,Rs,left=None,right=None) if True else None
for clock in ['video24','capture25']:
    tt=k/24.0 if clock=='video24' else n/25.0
    dt=1/24.0 if clock=='video24' else 1/25.0
    # extrapolate linearly outside
    R=np.interp(tt,ts,Rs); lo=tt<ts[0]; R[lo]=Rs[0]+(Rs[1]-Rs[0])/(ts[1]-ts[0])*(tt[lo]-ts[0])
    P=np.array([R[i]*ray(u[i],v[i]) for i in k])
    for tq in (0.3,0.6):
        i=int(np.argmin(np.abs(tt-tq))) if clock=='video24' else [j for j in k if n[j]==int(np.floor(tq*25+0.5))][0]
        vv=np.linalg.norm(P[i+1]-P[i])/(tt[i+1]-tt[i]); vv2=np.linalg.norm(P[i+2]-P[i+1])/(tt[i+2]-tt[i+1])
        a=np.linalg.norm((P[i+2]-P[i+1])/(tt[i+2]-tt[i+1])-(P[i+1]-P[i])/(tt[i+1]-tt[i]))/((tt[i+2]-tt[i])/2)
        print(f"{clock} t={tq} k{i}: v={vv:.3f} a_vec={a:.2f} a_speed={(vv2-vv)/((tt[i+2]-tt[i])/2):+.2f}  dR={100*(R[i+1]-R[i]):+.2f}cm")
