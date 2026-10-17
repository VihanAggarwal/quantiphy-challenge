import numpy as np
from pool3d import body,T,keep,e,n,c
import itertools
for f in [3470,3530,3590]:
  for fps in [24,25]:
    B,P=body(f,fps,ref=1)
    v=np.array([(e[0]-c[0])/f,(e[1]-c[1])/f,1.]); vh=v/np.linalg.norm(v)
    V=22.16*vh/fps  # per frame
    Pk=P[keep]; Bk=B[keep]
    # bbox centre in body coords -> camera coords
    up=np.array([0,-1,(e[1]-c[1])/f]); up/=np.linalg.norm(up); s=np.cross(vh,up); s/=np.linalg.norm(s); upo=np.cross(s,vh)
    ctr_b=(Bk.max(0)+Bk.min(0))/2
    ctr=ctr_b[0]*vh+ctr_b[1]*s+ctr_b[2]*upo
    for (F1,F2) in [(24,48),(25,50),(25,49)]:
        d1=np.linalg.norm(ctr+V*(F1-1)); d2=np.linalg.norm(ctr+V*(F2-1))
        th1=np.degrees(np.arccos((ctr+V*(F1-1))@vh/d1)); th2=np.degrees(np.arccos((ctr+V*(F2-1))@vh/d2))
        # where along fore axis must origin be (at bbox ctr lat/up) to give d1=102.6664 at F1
        # solve along vh: |ctr+V*(F1-1)+ a*vh|=102.6664
        p=ctr+V*(F1-1); bq=2*p@vh; cq=p@p-102.6664**2; a=(-bq+np.sqrt(bq*bq-4*cq))/2
        p2=ctr+V*(F2-1)+a*vh
        print(f,fps,(F1,F2),'bboxctr d1 %.2f d2 %.2f th1 %.2f th2 %.2f | origin shift along fore for d1: %.2f m -> d2 %.2f'%(d1,d2,th1,th2,a,np.linalg.norm(p2)))
