import numpy as np
cx,cy=960.0,977.0
def proj_aspect(f, vpx, hub=(1730.3,1165.0), Rpx=101.7, yh=990.0):
    # camera pitch from horizon: rotate so that horizon at yh
    pitch=np.arctan((yh-cy)/f)  # positive -> camera tilted up? (horizon below centre => looking up)
    # work in camera coords with world-horizontal axle; build world->cam rotation about x
    c,s=np.cos(pitch),np.sin(pitch)
    Rx=np.array([[1,0,0],[0,c,-s],[0,s,c]])
    # axle direction: VP at (vpx, yh) in image -> camera dir
    n=np.array([vpx-cx, yh-cy, f]); n/=np.linalg.norm(n)
    up_cam=Rx@np.array([0,-1,0.0])   # world up in camera coords (y down)
    up_cam/=np.linalg.norm(up_cam)
    # make n exactly horizontal (orthogonal to up)
    n=n-up_cam*(n@up_cam); n/=np.linalg.norm(n)
    e1=np.cross(up_cam,n); e1/=np.linalg.norm(e1)   # horizontal in wheel plane
    e2=up_cam
    Z=28.0
    C=np.array([(hub[0]-cx)/f*Z,(hub[1]-cy)/f*Z,Z])
    R=Rpx*Z/f
    t=np.linspace(0,2*np.pi,2000)
    P=C[None,:]+R*(np.cos(t)[:,None]*e1[None,:]+np.sin(t)[:,None]*e2[None,:])
    x=cx+f*P[:,0]/P[:,2]; y=cy+f*P[:,1]/P[:,2]
    w=x.max()-x.min(); h=y.max()-y.min()
    return w/h, w, h
for yh in (975,990,1005):
  for vpx in (640,694,730):
    print('yh',yh,'vpx',vpx, ' '.join('f=%d:%.4f'%(f,proj_aspect(f,vpx,yh=yh)[0]) for f in (1800,2100,2500,3000,3500,4140,5000)))
