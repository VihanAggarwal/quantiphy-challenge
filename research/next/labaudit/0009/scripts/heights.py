import numpy as np
f=711.;CX=640;CY=360
def u(x,y,ff=f):
    v=np.array([(x-CX)/ff,(y-CY)/ff,1.]);return v/np.linalg.norm(v)
def floor_below(P,d,R):
    b=P@d; c=P@P-R*R
    return -b+np.sqrt(b*b-c)
R0=1.321;RF=2.0285;R46=1.5795
for ff in [700,711,722]:
  P0=R0*u(482.5,185.8,ff); P46=R46*u(527.9,481.6,ff)
  dA=(P46-P0)/np.linalg.norm(P46-P0)
  for name,vp in [('A:P0->P46',None),('C:VP f0',(735,1902)),('C:VP f48',(734,1936))]:
    if vp is None: d=dA
    else:
        d=np.array([(vp[0]-CX)/ff,(vp[1]-CY)/ff,1.]);d/=np.linalg.norm(d)
    h0=floor_below(P0,d,RF)
    H46=h0-(P46-P0)@d
    # route B: bounce frame 37 centre; ball lowest point; use pixel y in [660,668], width-based range
    out=[]
    for y37 in [660,666,668.4]:
        v=u(547.1,y37,ff)
        # range from horizontal width 94px (tangential scale f/c)
        c=v[2]; alpha=47.0*c/ff; rng=0.116/np.sin(alpha)
        P37=rng*v
        h0B=(P37-P0)@d+0.116
        H46B=(P37-P46)@d+0.116
        out.append('y37=%.0f rng=%.3f h0=%.3f apex=%.3f'%(y37,rng,h0B,H46B))
    print('f=%d %-10s pitch=%.1f  A-floor: h0=%.4f apex=%.4f | B-bounce: %s'%(ff,name,np.degrees(np.arcsin(d[2])),h0,H46,' ; '.join(out)))
