# Reproduce 0169 astronaut speed/accel from tracks t169.txt (original, thr>60 blob) and t169s.txt (segmented twin).
# Route A: global smoothstep (2-key Blender Bezier ease) fit; Route B: free degree-5 polynomial.
# aB=(v(k)-v(k-1))*fps [centre k-1], aM [centre k-0.5], aF=(v(k+1)-v(k))*fps [centre k]; v(k)=|p(k)-p(k-1)|*fps.
import sys, numpy as np
sys.path.insert(0, __file__.rsplit('/',1)[0]); from lm import lsq
fps=24; s=2.2/89.5
S=lambda u: (lambda u: 3*u**2-2*u**3)(np.clip(u,0,1))
for fn in ['t169.txt','t169s.txt']:
    d=np.loadtxt(__file__.rsplit('/',1)[0]+'/'+fn); f=d[:,0]
    i6,i7=(6,7)
    cx,cy=d[:,i6],d[:,i7]
    p,_=lsq(lambda p: np.r_[p[2]+p[4]*S((f-p[0])/p[1])-cx, p[3]+p[5]*S((f-p[0])/p[1])-cy],[0,80,cx[0],cy[0],15,-280])
    A=lambda k: np.array([p[2]+p[4]*S((k-p[0])/p[1]), p[3]+p[5]*S((k-p[0])/p[1])])
    px,py=np.polyfit(f,cx,5),np.polyfit(f,cy,5)
    B=lambda k: np.array([np.polyval(px,k),np.polyval(py,k)])
    for nm,P in [('A smoothstep',A),('B poly5',B)]:
        v=lambda k: np.linalg.norm(P(k)-P(k-1))*fps*s
        print(fn,nm,' | '.join('t%.1f v=%.3f aB=%.3f aM=%.3f aF=%.3f'%(t,v(t*fps),(v(t*fps)-v(t*fps-1))*fps,(v(t*fps+.5)-v(t*fps-.5))*fps,(v(t*fps+1)-v(t*fps))*fps) for t in (0.5,1,2,3)))
