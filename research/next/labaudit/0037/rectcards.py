"""Rectify flat objects on the table plane (h=0.172) and fit min-area rectangles in metric coords."""
import cv2, numpy as np
F=711.0; CX,CY=640.,360.
n=np.load('plane.npy')
# in-plane axes
e1=np.cross(n,[0,0,1.0]); e1/=np.linalg.norm(e1); e2=np.cross(n,e1)
def to_plane(us,vs,h):
    R=np.stack([(us-CX)/F,(vs-CY)/F,np.ones_like(us)],1)
    s=h/(-(R@n)); X=R*s[:,None]
    return np.stack([X@e1,X@e2],1)
for vid in ('frames/vx_24.png','frames/vo_24.png','f40/vx_00.png'):
    f=cv2.imread(vid); hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    # flat playing card: whitish, region x 635..755, y 497..520
    win=np.zeros(f.shape[:2],bool); win[497:521,636:756]=True
    mcard=win&(hsv[...,1]<60)&(hsv[...,2]>150)
    # credit card: dark/blue+yellow, region x 505..622, y 525..556
    win2=np.zeros(f.shape[:2],bool); win2[525:557,505:623]=True
    mcc=win2&((hsv[...,2]<110)|((hsv[...,0]>15)&(hsv[...,0]<40)&(hsv[...,1]>120)))
    for name,m in (('flat card',mcard),('credit card',mcc)):
        m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
        nl,l,st,_=cv2.connectedComponentsWithStats(m)
        k=1+np.argmax(st[1:,4]); vs,us=np.where(l==k)
        for h in (0.169,0.172,0.176):
            Q=to_plane(us.astype(float),vs.astype(float),h).astype(np.float32)
            (cx,cy),(a,b),ang=cv2.minAreaRect(Q)
            print('%-16s %-11s h=%.3f px=%4d  rect %.2f x %.2f cm  area-based %.1f cm2'%(vid,name,h,len(us),max(a,b)*100,min(a,b)*100,len(us)*0))
