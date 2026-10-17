"""Size route for the radial steps: smooth local fits of size-based centre range (three size measures).
Near side (t=0.6, c15->c16): even quartic/quadratic around the turning point over c12-c24.
Far side (t=0.3, c8->c9): quadratic/cubic over c4-c12."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
B='/home/user/quantiphy-challenge/research/next/labaudit2/0010/'
S=json.load(open(B+'size_s.json')); Cc=json.load(open(B+'circ.json'))
k=np.arange(49); n=np.array([cap(i) for i in k])
meas={'halfmax':np.array([S[i]['wh'] for i in k]),'s_circle':np.array([Cc[i]['s']['d'] for i in k]),'X_circle':np.array([Cc[i]['X']['d'] for i in k])}
def fitpoly(c,R,deg,cen):
    A=np.vander(c-cen,deg+1); p,*_=np.linalg.lstsq(A,R,rcond=None); return lambda x: np.vander(np.atleast_1d(x)-cen,deg+1)@p
for nm,wd in meas.items():
    R=F*0.07/wd
    # near side
    for lo,hi,deg in [(13,23,2),(12,24,2),(13,23,3),(12,24,4),(14,22,2)]:
        sel=(n>=lo)&(n<=hi)&~((nm=='X_circle')&(k<12))
        f=fitpoly(n[sel],R[sel],deg,18.0)
        d=(f(16)-f(15))[0]*100; d2=(f(17)-f(16))[0]*100
        cc=np.linspace(13,23,1001); cmin=cc[np.argmin(f(cc))]
        print(f"{nm:9s} near c{lo}-{hi} deg{deg}: dR(15->16) {d:+.2f}cm dR(16->17) {d2:+.2f}  turning c{cmin:.2f}  rel scale R15 {f(15)[0]:.3f}")
    for lo,hi,deg in [(4,11,2),(3,11,3),(5,13,2) ]:
        sel=(n>=lo)&(n<=hi)
        if nm=='X_circle': sel&=False
        if sel.sum()<4: continue
        f=fitpoly(n[sel],R[sel],deg,8.0)
        print(f"{nm:9s} far  c{lo}-{hi} deg{deg}: dR(7->8) {(f(8)-f(7))[0]*100:+.2f} dR(8->9) {(f(9)-f(8))[0]*100:+.2f} dR(9->10) {(f(10)-f(9))[0]*100:+.2f} R8 {f(8)[0]:.3f}")
