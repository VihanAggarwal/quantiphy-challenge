from common import *
def topview(img, f, cx, cy, R, H, Xr, Yr, res):
    # R: world->camera rotation (rows = camera axes x(right), y(down), z(forward) in world coords); camera at (0,0,H); ground Z=0
    Xs=np.arange(Xr[0],Xr[1],res); Ys=np.arange(Yr[1],Yr[0],-res)
    XX,YY=np.meshgrid(Xs,Ys)
    P=np.stack([XX,YY,-H*np.ones_like(XX)],-1)
    pc=P@R.T
    u=cx+f*pc[...,0]/pc[...,2]; v=cy+f*pc[...,1]/pc[...,2]
    u[pc[...,2]<=0]=-1
    return cv2.remap(img,u.astype(np.float32),v.astype(np.float32),cv2.INTER_LINEAR,borderValue=(255,255,255))
def R_pitch(theta, yaw=0.0, roll=0.0):
    # camera forward tilted down by theta, rotated by yaw about world Z, roll about forward
    fw=np.array([np.sin(yaw)*np.cos(theta), np.cos(yaw)*np.cos(theta), -np.sin(theta)])
    rt=np.array([np.cos(yaw), -np.sin(yaw), 0.0])
    dn=np.cross(fw,rt)
    # roll
    c,s=np.cos(roll),np.sin(roll); rt2=c*rt+s*dn; dn2=-s*rt+c*dn
    return np.array([rt2,dn2,fw])
