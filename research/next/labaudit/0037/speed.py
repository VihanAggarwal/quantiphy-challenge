import numpy as np, sys
from track3d import track, P, F
FPS=24.0
for v in sys.argv[1:] or ['x']:
    T=track(v); mi=T[:,3]
    # Z model 1: local linear fit of 1/minor (Z linear in t) in +-5 frames; model 2: global quadratic of minor
    def zloc(i,k,w=5):
        idx=np.arange(max(12,i-w),min(48,i+w)+1)
        good=idx[np.abs(mi[idx]-np.median(mi[idx]))<4]
        p=np.polyfit(good,k/mi[good],1); return np.polyval(p,i),p[0]
    r24=np.linalg.norm([(T[24,1]-640)/F,(T[24,2]-360)/F,1])
    kA=None
    _,_=0,0
    # calibrate route A: Z(24)=1.055/r24 using local fit with k=1
    z1,_=zloc(24,1.0); kA=(1.055/r24)/z1; kB=F*0.04
    print(v,'kA/kB=%.3f (stated depth vs 4cm size)'%(kA/kB))
    for name,k in (('A',kA),('B',kB)):
        X=np.array([P(T[i,1],T[i,2],zloc(i,k)[0]) for i in range(12,49)]); X=np.vstack([np.full((12,3),np.nan),X])
        def sp(i,j): return np.linalg.norm(X[j]-X[i])/((j-i)/FPS)*100
        for t,fr in ((1.0,24),(1.4,33.6)):
            i0=int(np.floor(fr)); i1=int(round(fr))
            print(' %s t=%.1f  fwd(%d->%d)=%.1f fwd(%d->%d)=%.1f  bwd(%d)=%.1f  central(%d)=%.1f central(%d)=%.1f  2-frame(%d->%d)=%.1f'%(name,t,i0,i0+1,sp(i0,i0+1),i0+1,i0+2,sp(i0+1,i0+2),i1,sp(i1-1,i1),i0,sp(i0-1,i0+1),i0+1,sp(i0,i0+2),i0-1,i0+2,sp(i0-1,i0+2)))
        # component breakdown at 24 and 33.5
        for i in (24,33):
            d=(X[i+1]-X[i])*FPS*100; print('   comp %d->%d (cm/s) x=%.1f y=%.1f z=%.1f'%(i,i+1,*d))
