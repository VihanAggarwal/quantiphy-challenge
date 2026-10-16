import numpy as np
CX,CY=640,360
def ray(u,v,f):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
vpv=np.array([452.6,1379.1]); vpc=np.array([2194.6,121.2]); vpj=np.array([219.5,-241.0])
for f in [650,711,760,800,850]:
    dn=ray(*vpv,f)
    hc=ray(*vpc,f); hj=ray(*vpj,f)
    # ball: size-implied centre distance: tangential px 59.5 ~ 2*f*tan(asin(R/d))/cos(theta)
    th=np.arccos(ray(985.8,369.6,f)[2])
    R=0.116; px=59.5
    a=np.arctan(px*np.cos(th)/(2*f)); d_size=R/np.sin(a)
    Pb=2.082*ray(666.4,617.9,f); H=Pb@dn+0.018
    zc=H-2.516*ray(564.3,424,f)@dn
    zb=H-(2.925+R)*ray(985.8,369.6,f)@dn
    zbs=H-d_size*ray(985.8,369.6,f)@dn
    zbin=H-2.73*ray(797.7,379.5,f)@dn
    print(f,'vert.carpet %.3f vert.junc %.3f'%(dn@hc,dn@hj),'H %.3f cup z %.3f ball z(stated) %.3f ball d_size %.3f z(size) %.3f bin z %.3f'%(H,zc,zb,d_size,zbs,zbin))
