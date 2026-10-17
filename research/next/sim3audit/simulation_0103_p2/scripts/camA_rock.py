import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *; from geom import *; from cam import *
fr=frames('simulation_0027_segmented',[24])
m=fgmask(fr[24]); m[320:]=False
cs,_=cv2.findContours(m.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cs,key=cv2.contourArea)[:,0,:].astype(float)
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/rockA_contour.npy',c)
L=c[np.argmin(c[:,0])]; R=c[np.argmax(c[:,0])]; print('extremes',L,R)
for f in [3401,3460,3517]:
  for p in [17.5,19.0,20.5]:
    hb=cam_from_object(f,480,480,p,(612,600),90.1103,'range')
    cam=Cam(f,480,480,p,hb+1.0)
    P1=P3((612,600),90.1103,f,480,480); P2=P3((612-155.43,600-6.03),90.4360,f,480,480)
    e1=cam.cam2world_vec(P2-P1); vz=e1[2]; e1[2]=0; e1/=np.linalg.norm(e1); e2=np.array([-e1[1],e1[0],0])
    out=[]
    for zr in [3.0,5.0,7.0]:
        GL=cam.ground(*L,zr); GR=cam.ground(*R,zr)
        out.append('z%.0f: e1 %.2f camx %.2f rngL %.1f'%(zr,abs((GR-GL)@e1),abs(GR[0]-GL[0]),np.linalg.norm(GL-cam.C)))
    # near base point (707,310) on plateau z=2.3
    NB=cam.ground(707,310,2.3)
    print(f,p,'h=%.1f'%cam.h,'boat vz %.2f'%vz,'e1 vs camx %.1f'%np.degrees(np.arctan2(e1[1],e1[0])),' | '.join(out),'| nearbase dist %.1f'%np.hypot(*NB[:2]))
