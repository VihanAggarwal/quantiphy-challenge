import numpy as np, json
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work/'
vD=np.load(W+'vp.npy'); vL=np.load(W+'vL.npy')
C=np.array([1280.,720.])
def cam(f):
    K=np.array([[f,0,C[0]],[0,f,C[1]],[0,0,1]]); Ki=np.linalg.inv(K)
    D=Ki@np.r_[vD,1]; D/=np.linalg.norm(D)
    L=Ki@np.r_[vL,1]; L/=np.linalg.norm(L)
    L=L-(L@D)*D; L/=np.linalg.norm(L)
    U=np.cross(D,L)  # check sign: up should have negative y (image up)
    if U[1]>0: U=-U
    return K,Ki,D,L,U
def ray(Ki,x):
    r=Ki@np.r_[x,1]; return r/np.linalg.norm(r)
def tri(track,f,kref=24,vfac=1.0):
    """track: dict k->(x,y). returns Q_ref (3D in units of V*1s) at frame kref, and residual px"""
    K,Ki,D,L,U=cam(f)
    A=[];b=[]
    for k,x in track.items():
        r=ray(Ki,np.array(x)); Rx=np.array([[0,-r[2],r[1]],[r[2],0,-r[0]],[-r[1],r[0],0]])
        c=(k-kref)/24.0*vfac
        A.append(Rx); b.append(-c*(Rx@D))
    A=np.vstack(A); b=np.concatenate(b)
    Q=np.linalg.lstsq(A,b,rcond=None)[0]
    # reprojection residual
    res=[]
    for k,x in track.items():
        P=Q+(k-kref)/24.0*vfac*D; p=K@P; p=p[:2]/p[2]; res.append(np.linalg.norm(p-np.array(x)))
    return Q,np.sqrt(np.mean(np.square(res)))
