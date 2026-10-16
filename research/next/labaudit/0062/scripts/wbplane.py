import numpy as np, json
from common import *
Q={int(k):np.array(v) for k,v in json.load(open(O+'wbquads.json')).items()}
def canon(c):
    # order around centroid, start at far-left (smallest y among left half)
    cen=c.mean(0); ang=np.arctan2(c[:,1]-cen[1],c[:,0]-cen[0]); c=c[np.argsort(ang)]
    # ang sorted: from -pi.. ; choose start = point with min (x+y)?? use far edge: two smallest y
    i=np.argmin(c[:,0]+0.0*c[:,1])
    return np.roll(c,-i,axis=0)
for n in Q: Q[n]=canon(Q[n])
def normal(pitch,roll):
    # floor normal in camera coords (x right, y down, z fwd); camera pitched down by pitch
    p,r=np.radians(pitch),np.radians(roll)
    n=np.array([0,np.cos(p),np.sin(p)])  # 'down' direction... floor normal pointing down from camera
    # roll about z
    R=np.array([[np.cos(r),-np.sin(r),0],[np.sin(r),np.cos(r),0],[0,0,1]])
    return R@n
def backproj(c,nrm,h,f=F):
    d=np.c_[(c[:,0]-CX)/f,(c[:,1]-CY)/f,np.ones(len(c))]
    t=h/(d@nrm); return d*t[:,None]
def geom(c,nrm,h=1.0,f=F):
    P=backproj(c,nrm,h,f)
    s=[np.linalg.norm(P[(i+1)%4]-P[i]) for i in range(4)]
    cos=[]
    for i in range(4):
        a=P[i-1]-P[i]; b=P[(i+1)%4]-P[i]; cos.append(a@b/np.linalg.norm(a)/np.linalg.norm(b))
    return np.array(s),np.array(cos),P
frames=[n for n in range(20,49)]
def res(x,f=F):
    nrm=normal(x[0],x[1]); R=[]
    S=[]
    for n in frames:
        s,cs,_=geom(Q[n],nrm,1.0,f); R+=list(cs*3); S.append(s)
    S=np.array(S)
    # lengths constant: compare each frame's mean of opposite sides to global mean
    L1=(S[:,0]+S[:,2])/2; L2=(S[:,1]+S[:,3])/2
    R+=list((L1/L1.mean()-1)); R+=list((L2/L2.mean()-1))
    R+=list((S[:,0]-S[:,2])/L1); R+=list((S[:,1]-S[:,3])/L2)
    return np.array(R)
for f in (690,700,711,722,735):
    best=None
    for p in np.arange(10,80,1.0):
        for r in np.arange(-15,15,1.0):
            c=np.sum(res([p,r],f)**2)
            if best is None or c<best[0]: best=(c,p,r)
    for step in (0.3,0.1,0.03):
        c0,p0,r0=best
        for p in np.arange(p0-3*step*3,p0+3*step*3+1e-9,step):
            for r in np.arange(r0-3*step*3,r0+3*step*3+1e-9,step):
                c=np.sum(res([p,r],f)**2)
                if c<best[0]: best=(c,p,r)
    class S_: pass
    sol=S_(); sol.x=np.array(best[1:]); sol.cost=best[0]
    nrm=normal(*sol.x)
    S=np.array([geom(Q[n],nrm,1.0,f)[0] for n in frames]); C=np.array([geom(Q[n],nrm,1.0,f)[1] for n in frames])
    L1=(S[:,0]+S[:,2])/2; L2=(S[:,1]+S[:,3])/2
    print('f=%d pitch=%.2f roll=%.2f cost=%.4f  ratio L1/L2=%.3f  |cos| mean=%.3f  L1 cv=%.3f L2 cv=%.3f'%(f,sol.x[0],sol.x[1],sol.cost,(L1/L2).mean(),np.abs(C).mean(),L1.std()/L1.mean(),L2.std()/L2.mean()))
    if f==711:
        for k,n in enumerate(frames): print(n,np.round(S[k],3),np.round(C[k],3))
np.save(O+'wbQ.npy',np.array([Q[n] for n in range(17,49)]))
