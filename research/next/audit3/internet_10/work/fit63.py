import numpy as np
k=np.arange(42,52)
# from bg.py output 0063 frames 42-51 bbox right edge (leading) and left edge
R=np.array([414,454,503,561,632,714,810,917,1036,1168.])
L=np.array([189,253,306,364,438,530,632,749,867,986.])
C=np.array([320.9,363.9,412.7,470.5,546.9,636.3,737.1,851.4,964.5,1098.9])
def model(par,t):
    g,c,t0,x0=par
    tt=np.clip(t-t0,0,None)
    if c<=1e-9: return x0+0.5*g*tt**2
    vt=np.sqrt(g/c); return x0+(vt**2/g)*np.log(np.cosh(g*tt/vt))
for name,x,lo in [('R',R,43),('L',L,43),('C',C,43),('R44',R,44)]:
    s=k>=lo; kk=k[s]; xx=x[s]
    p=np.polyfit(kk,xx,2); print(name,'quad a=%.2f vertex %.2f'%(2*p[0],-p[1]/(2*p[0])))
    best=None
    for g in np.arange(8,16,0.05):
        for c in [0,5e-5,1e-4,2e-4,3e-4,5e-4]:
            for t0 in np.arange(36,44,0.05):
                m0=model([g,c,t0,0],kk); x0=np.mean(xx-m0); e=np.sqrt(np.mean((m0+x0-xx)**2))
                if best is None or e<best[0]: best=(e,g,c,t0)
    print(name,'best fit rms %.2f g=%.2f c=%.4g t0=%.2f'%best)
    b0=None
    for g in np.arange(8,16,0.02):
        for t0 in np.arange(36,44,0.02):
            m0=model([g,0,t0,0],kk); x0=np.mean(xx-m0); e=np.sqrt(np.mean((m0+x0-xx)**2))
            if b0 is None or e<b0[0]: b0=(e,g,t0)
    print(name,'no-drag from-rest rms %.2f g=%.2f t0=%.2f'%b0)
