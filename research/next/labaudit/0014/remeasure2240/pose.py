import cv2,numpy as np
f=711.0; K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
img=np.array([[446.5,343],[659,310],[728,455.5],[425.5,500]],float) # FL FR NR NL
def solve(W,D):
    obj=np.array([[0,D,0],[W,D,0],[W,0,0],[0,0,0]],float) # x right, y far
    ok,r,t=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    R,_=cv2.Rodrigues(r); pr,_=cv2.projectPoints(obj,r,t,K,None)
    err=np.abs(pr.reshape(-1,2)-img).max()
    n=R[:,2]; d=n@t.ravel()
    return R,t.ravel(),err
for W,D in [(76.0,60.3),(60.3,76.0)]:
    R,t,err=solve(W,D)
    n=R[:,2]; 
    def hit(u,v,h=0):
        ray=np.array([(u-640)/f,(v-360)/f,1.]); 
        # plane n.X = n.t + h (h above table toward camera side)
        s=(n@t - h*np.sign(n@t))/(n@ray) if False else None
        return ray
    print('W,D',W,D,'maxreproj',err,'t',t, 'tilt deg',np.degrees(np.arccos(abs(n[2]))))
    np.save('pose_%d.npy'%W,np.hstack([R.ravel(),t]))
