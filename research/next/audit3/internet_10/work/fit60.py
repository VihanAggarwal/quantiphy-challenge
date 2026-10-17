import numpy as np
import itertools
fps=22000/733
k=np.arange(53,65)
L=np.array([64,98,146,206,278,361,457,564,681,807,942,1088.])
R=np.array([184,219,266,326,399,482,579,685,804,932,1068,1216.])
M=(L+R)/2
for name,x in [('L',L),('R',R),('M',M)]:
    for lo,hi in [(53,64),(53,58),(59,64),(55,64)]:
        s=(k>=lo)&(k<=hi); p=np.polyfit(k[s],x[s],2)
        print(name,lo,hi,'a=%.2f px/fr^2'%(2*p[0]), 'vertex frame %.2f'%(-p[1]/(2*p[0])), 'v(60.03)=%.1f'%(2*p[0]*60.03+p[1]))
# drag model x'' = g - c v^2 from rest at t0 at x0
def model(par,t):
    g,c,t0,x0=par
    tt=np.clip(t-t0,0,None)
    if c<=1e-9: return x0+0.5*g*tt**2
    vt=np.sqrt(g/c)
    return x0+(vt**2/g)*np.log(np.cosh(g*tt/vt))

for name,x in [('M',M),('L',L),('R',R)]:
    best=None
    for g in np.arange(9,16,0.05):
        for c in [0,1e-4,2e-4,3e-4,4e-4,5e-4,6e-4,8e-4,1e-3,1.2e-3,1.5e-3,2e-3]:
            for t0 in np.arange(48,53,0.05):
                m0=model([g,c,t0,0],k); x0=np.mean(x-m0); e=np.sqrt(np.mean((m0+x0-x)**2))
                if best is None or e<best[0]: best=(e,g,c,t0)
        pass
    print(name,'best drag fit rms %.2f g=%.2f c=%.4g t0=%.2f'%best)
    b0=None
    for g in np.arange(9,16,0.02):
        for t0 in np.arange(46,53,0.02):
            m0=model([g,0,t0,0],k); x0=np.mean(x-m0); e=np.sqrt(np.mean((m0+x0-x)**2))
            if b0 is None or e<b0[0]: b0=(e,g,t0)
    print(name,'no-drag from-rest fit rms %.2f g=%.2f t0=%.2f'%b0)
