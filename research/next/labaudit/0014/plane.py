import numpy as np, cv2
def L(name):
    p,d=np.load(f'edge_{name}.npy'); return np.cross([p[0],p[1],1],[p[0]+d[0],p[1]+d[1],1])
def X(a,b):
    h=np.cross(L(a),L(b)); return h[:2]/h[2]
C={'FL':X('left','front'),'FR':X('right','front'),'BR':X('right','back'),'BL':X('left','back')}
for k,v in C.items(): print(k,np.round(v,1))
def pose(f, W=0.760, D=0.603):
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    obj=np.array([[0,0,0],[W,0,0],[W,D,0],[0,D,0]],float)  # FL,FR,BR,BL ; x along front edge, y toward back
    img=np.array([C['FL'],C['FR'],C['BR'],C['BL']],float)
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    Rm,_=cv2.Rodrigues(rv)
    proj,_=cv2.projectPoints(obj,rv,tv,K,None)
    err=np.abs(proj.reshape(-1,2)-img).max()
    return Rm,tv.ravel(),err
if __name__=='__main__':
    # check orthogonality: VPs
    def vp(a,b):
        h=np.cross(L(a),L(b)); return h
    v1=vp('left','right'); v2=vp('front','back')
    print('vp1',v1[:2]/v1[2],'vp2',v2[:2]/v2[2] if abs(v2[2])>1e-9 else v2)
    # f from orthogonality: (v1-c).(v2-c) + f^2 = 0 with homogeneous
    a=v1[:2]/v1[2]-[640,360]; b=v2[:2]/v2[2]-[640,360]
    print('f from VP orthogonality', np.sqrt(max(-(a@b),0)))
    for f in [690,711,730]:
        Rm,t,err=pose(f)
        n=Rm[:,2]
        print(f,'t',np.round(t,3),'normal',np.round(n,3),'reproj err',round(err,2),'dist FL',np.linalg.norm(t))
