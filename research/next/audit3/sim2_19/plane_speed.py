import numpy as np
from common import frames
from tmpl import track
for v,box0,f0,s0 in [('simulation_0284',(1000,600,1500,880),30,-34.4),('simulation_0286',(1000,600,1500,880),30,-34.4),
                     ('simulation_0285',(1150,330,1650,500),30,-43),('simulation_0287',(1150,330,1650,500),30,-43)]:
    fr=frames(v)
    out=[]
    for k in [-12,-8,-4,4,8,12,16]:
        dx,dy,mv=track(fr,f0,box0,f0+k,s0*k,search=40)
        out.append((k,round(dx,2),round(dy,2),round(mv,3),round(dx/k,3)))
    ks=np.array([o[0] for o in out]); dxs=np.array([o[1] for o in out])
    print(v, out, 'slope', np.polyfit(ks,dxs,1)[0])
