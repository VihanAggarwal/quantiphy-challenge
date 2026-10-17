"""Label-style FD values on the capture clock from the geometric (sphere) range route.
t=0.3 -> c8 (k8), t=0.6 -> c15 (k14).  v(t)=25|P(k+1)-P(k)|; a(t)=625|P(k+2)-2P(k+1)+P(k)| (vector) and 25(|v(k+1)|-|v(k)|)."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
from geo import *
def calib(kind):
    if kind=='anch_ceil':
        idx=[(8,1.706),(14,1.344),(29,1.784),(36,1.717),(43,1.350)]
        def cost(d0,L):
            R,D=ranges(d0,L); return sum((R[i]-0.035-s)**2 for i,s in idx)
    elif kind=='anch_treal':
        idx=[(7,1.706),(14,1.344),(29,1.784),(36,1.717),(43,1.350)]
        def cost(d0,L):
            R,D=ranges(d0,L); return sum((R[i]-0.035-s)**2 for i,s in idx)
    elif kind=='size':
        good=np.array([not (11<=nn<=14 or 21<=nn<=24 or 41<=nn<=44) for nn in n])
        def cost(d0,L):
            R,D=ranges(d0,L); return np.sum(((F*0.07/R-w)[good])**2)
    c,d0,L=grid_fit(cost,d0s=np.arange(1.40,1.65,0.0025),Ls=np.arange(0.30,0.40,0.0005))
    return d0,L
STK={8:1.706,14:1.344}   # stated surface range at the label frames (t=0.3->k8, t=0.6->k14)
def label(R, k0, s0, mode, bias=0.0, uu=u, vv=v):
    P={}
    for j in range(3):
        kk=k0+j
        if j==0: rs=s0
        elif mode=='persist': rs=s0+(R[kk]-R[k0])
        else: rs=R[kk]-0.035+bias
        P[j]=rs*ray(uu[kk],vv[kk])
    v1=25*np.linalg.norm(P[1]-P[0]); v2=25*np.linalg.norm(P[2]-P[1])
    a_vec=625*np.linalg.norm(P[2]-2*P[1]+P[0]); a_sp=25*(v2-v1)
    return v1,a_vec,a_sp,v2
if __name__=='__main__':
    out={}
    for kind in ['anch_ceil','anch_treal','size']:
        d0,L=calib(kind); R,D=ranges(d0,L)
        anchors=[(8,1.706),(14,1.344),(29,1.784),(36,1.717),(43,1.350)]
        bias=np.mean([s-(R[i]-0.035) for i,s in anchors])
        print(f"== {kind}: d0={d0:.4f} L={L:.4f} mean ToF-model bias {bias*100:+.2f}cm")
        print("   centre ranges k6..k17:",' '.join(f"{R[i]:.4f}" for i in range(6,18)))
        print("   radial steps (cm) k6..k17:",' '.join(f"{(R[i+1]-R[i])*100:+.2f}" for i in range(6,17)))
        for t,k0 in [(0.3,8),(0.6,14)]:
            for mode in ['persist','meanbias']:
                v1,av,asp,v2=label(R,k0,STK[k0],mode,bias)
                print(f"   t={t} k{k0} {mode:8s}: v={v1:.3f}  a_vec={av:.2f}  a_speed={asp:+.2f}  (v next {v2:.3f})")
        # physical: centre track, central/forward differences
        C=np.array([R[i]*ray(u[i],v[i]) for i in range(49)])
        for t,k0 in [(0.3,8),(0.6,14)]:
            fd=25*np.linalg.norm(C[k0+1]-C[k0]); cd=25*np.linalg.norm(C[k0+1]-C[k0-1])/2
            print(f"   physical-ish centre track t={t}: FD {fd:.3f}  central {cd:.3f}  a_vec(FD2) {625*np.linalg.norm(C[k0+2]-2*C[k0+1]+C[k0]):.2f}  a_central {625*np.linalg.norm(C[k0+1]-2*C[k0]+C[k0-1]):.2f}")
        out[kind]=dict(d0=d0,L=L,R=R.tolist(),bias=bias)
    json.dump(out,open(B+'geo_ranges.json','w'))
