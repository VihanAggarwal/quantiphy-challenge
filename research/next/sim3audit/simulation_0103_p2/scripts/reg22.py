import numpy as np, sys, cv2
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from vhull import *; from track import *
np.set_printoptions(precision=2,suppress=True)
im=frames('simulation_0022_segmented',[24])[24]; m=fgmask(im); m[:, 565:]=False; m[:500]=False
n,l,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8)); k=1+np.argmax(st[1:,4]); M22=(l==k)
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/M22.npy',M22)
ys,xs=np.where(M22); print('0022 rock bbox',xs.min(),xs.max(),ys.min(),ys.max())
for f22,p22,b1 in [(4513,-1.25,(864,638)),(4347,-1.25,(860,638)),(4625,-1.25,(866.3,638.6)),(4513,-1.76,(864,638)),(4513,-0.5,(864,638))]:
    b2=(753.9,638.6)
    R22=Reg(f22,480,480,p22,b1,b2,148.7451,146.9726)
    camW=R22.cam_W()
    print('f22',f22,'p22',p22,'cam22 W',camW)
    # rock: footprint center approx (1.5,-42,0); distances
    for pt in [(1.5,-42,0),(1.5,-30,0),(1.5,-55,0)]:
        d=np.linalg.norm(np.array(pt)-camW); uv=R22.project_W(np.array(pt,float)); print('   pt',pt,'dist %.1f'%d,'proj',np.round(uv,1))
