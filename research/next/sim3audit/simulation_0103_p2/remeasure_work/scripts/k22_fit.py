import numpy as np
from reg import *
from rockmask import rock_mask
Q=np.load(W+'c2_footprint_boatframe.npy')
m,c=rock_mask('0022_segmented',0)
cols=np.arange(40,556,5)
top=np.array([np.nonzero(m[:,x])[0].min() for x in cols]); bot=np.array([np.nonzero(m[:,x])[0].max() for x in cols])
obs_l, obs_r = np.nonzero(m.any(0))[0][[0,-1]]
def analyze(f22,d22,yaw_px=0.0,zs=1.0,verbose=False):
    F=frame_of('K22',f=f22,d=d22,a1=(865+yaw_px,640))
    uv,z=project(F,Q)
    # for each column: ray plane intersection with footprint: find footprint points near the column's vertical plane
    Cb=F['C']
    res=[]
    for x,t0,b0 in zip(cols,top,bot):
        # vertical plane through camera containing ray at column x
        rb=F['M']@F['cam'].ray(x,480.)
        # footprint points whose projection u within 3px of x
        sel=np.abs(uv[:,0]-x)<3
        if sel.sum()<2: res.append((x,np.nan,np.nan,np.nan)); continue
        dist=np.linalg.norm((Q[sel]-Cb)[:,:2],axis=1)
        dn,dfar=dist.min(),dist.max()
        # base ray at bottom contour: height at near footprint distance
        def zat(v,D):
            r=F['M']@F['cam'].ray(x,v); s=D/np.linalg.norm(r[:2]); return Cb[2]+s*r[2]
        res.append((x, zat(b0,dn), zat(t0,dn), zat(t0,0.5*(dn+dfar))))
    res=np.array(res)
    return F,uv,res
if __name__=='__main__':
    for f22 in [4350,4500]:
      for d22 in [-0.5,-0.7,-0.9]:
        F,uv,res=analyze(f22,d22)
        ok=~np.isnan(res[:,1])
        print('f %d d %.1f proj x %.0f..%.0f (obs %d..%d) | base z med %.2f | top z (near-dist) max %.2f | top z (mid-dist) max %.2f | cam z %.2f'%(f22,d22,uv[:,0].min(),uv[:,0].max(),obs_l,obs_r,np.median(res[ok,1]),np.nanmax(res[:,2]),np.nanmax(res[:,3]),F['C'][2]))
