import numpy as np
from common import *
exec(open('wbplane.py').read().split('frames=[n')[0])
vp=np.array([467,1363.0])
d=np.r_[(vp-[CX,CY])/F,1]; nm_seam=d/np.linalg.norm(d)
nm_board=normal(38.93,8.53)
print('angle deg',np.degrees(np.arccos(nm_seam@nm_board)))
for name,nm in [('board',nm_board),('seam',nm_seam)]:
    S=np.array([geom(Q[n],nm,1.0)[0] for n in range(20,49)]); C=np.array([geom(Q[n],nm,1.0)[1] for n in range(20,49)])
    W=(S[:,0]+S[:,2])/2; L=(S[:,1]+S[:,3])/2
    dd=np.r_[(np.array([704.8,409.8])-[CX,CY])/F,1]; dh=dd/np.linalg.norm(dd)
    h=2.815*(dh@nm)
    print(name,'W/h=%.4f (cv %.3f) L/h=%.4f (cv %.3f) |cos|=%.3f  h(board ToF)=%.3f -> W=%.1f L=%.1f'%(W.mean(),W.std()/W.mean(),L.mean(),L.std()/L.mean(),np.abs(C).mean(),h,W.mean()*h*100,L.mean()*h*100))
    # bag h from stated
    for k,uv,st,dz in [('bag',(837.4,329.2),3.307,0),('mario',(635.1,623.8),2.016,0.05)]:
        dd=np.r_[(np.array(uv)-[CX,CY])/F,1]; dh=dd/np.linalg.norm(dd); print('   h from',k,'%.3f'%(st*(dh@nm)+dz))
