import numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/'
F=711.; CX=640.; CY=360.
p=np.load(D+'scripts/table_pose_711.npy'); R=p[:9].reshape(3,3); T=p[9:]
n=R[:,2]  # table normal in camera coords (sign?)
if n@(-T)<0: n=-n  # normal pointing toward camera side
def ray(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.]); return d/np.linalg.norm(d)
def on_plane(u,v,h=0.0):
    """intersect ray with plane parallel to table at height h (m) above the table top"""
    d=ray(u,v); # plane: n.(X - T) = h
    s=(h+n@T)/(n@d); return s*d
def to_table(X):
    return R.T@(X-T)
cam_h=abs(n@T)
if __name__=='__main__':
    print('camera height above table top (m):',round(-(n@T) if n@T<0 else n@T,4), 'n',np.round(n,3))
    for nm,(u,v) in {'L':(411.3,465.5),'F':(644.4,575.4),'R':(1140.5,489.3)}.items():
        X=on_plane(u,v); print(nm,np.round(to_table(X),3),'range',round(np.linalg.norm(X),3))
