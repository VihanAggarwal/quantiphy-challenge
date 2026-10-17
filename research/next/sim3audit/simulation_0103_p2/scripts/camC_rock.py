import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *; from geom import *; from cam import *
fr=frames('simulation_0043_segmented',[24])
m=fgmask(fr[24]); m[470:]=False
cs,_=cv2.findContours(m.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cs,key=cv2.contourArea)[:,0,:].astype(float)
print('rock bbox',c[:,0].min(),c[:,0].max(),c[:,1].min(),c[:,1].max())
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/rockC_contour.npy',c)
for f in [3800,3870,3950]:
  for conv,p in [('range',53.5),('z',51.0),('range',55.0),('z',49.5)]:
    hb=cam_from_object(f,540,540,p,(357,915),173.7093,conv)
    for zr in [2.0,4.0]:   # height above water at which silhouette is mapped
        cam=Cam(f,540,540,p,hb+1.0)   # boat origin ~1 m above water
        # boat direction: from boat track in camera frame
        P1=P3((359,925),173.7093,f,540,540,conv); P2=P3((359-85.73,925-24.81),174.5515,f,540,540,conv)
        e1=cam.cam2world_vec(P2-P1); e1[2]=0; e1/=np.linalg.norm(e1); e2=np.array([-e1[1],e1[0],0])
        G=np.array([cam.ground(u,v,zr) for u,v in c])
        a=G@e1; b=G@e2; xw=G[:,0]
        print(f,conv,p,'h=%.1f'%cam.h,'z0',zr,'ext e1 %.2f e2 %.2f camx %.2f camy %.2f'%(a.ptp() if hasattr(a,'ptp') else a.max()-a.min(), b.max()-b.min(), xw.max()-xw.min(), G[:,1].max()-G[:,1].min()), 'e1 angle vs camx %.1f'%np.degrees(np.arctan2(e1[1],e1[0])))
