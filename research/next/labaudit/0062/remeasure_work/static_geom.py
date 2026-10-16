import numpy as np
cx=640.; cy=360.
def h(p): return np.array([p[0],p[1],1.])
for fn in ['static_corners.npy','static_corners65.npy']:
    Q=np.load(fn)
    for f in [680,711,740]:
        Kinv=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1]]))
        p=[h(q) for q in Q]
        v1=np.cross(np.cross(p[0],p[1]),np.cross(p[3],p[2])); v2=np.cross(np.cross(p[1],p[2]),np.cross(p[0],p[3]))
        d1=Kinv@v1; d2=Kinv@v2; d1/=np.linalg.norm(d1); d2/=np.linalg.norm(d2)
        n=np.cross(d1,d2); n/=np.linalg.norm(n); n= n if n[1]>0 else -n
        for lab,nn in [('own',n),('fit711',np.load('n_fit_711.npy')[:3])]:
            X=[]
            for q in p:
                r=Kinv@q; X.append(r/(nn@r))
            X=np.array(X); s=[np.linalg.norm(X[(k+1)%4]-X[k]) for k in range(4)]
            ang=np.degrees(np.arccos(((X[1]-X[0])@(X[3]-X[0]))/s[0]/s[3]))
            print(fn,f,lab,'cos(d1,d2)',round(abs(d1@d2),3),'n',np.round(nn,3),'far,right,near,left /h',np.round(s,4),'FL angle',round(ang,1))
    # f solving orthogonality
    v1=v1/v1[2]; v2=v2/v2[2]
    print(' f_ortho',np.sqrt(max(0,-((v1[0]-cx)*(v2[0]-cx)+(v1[1]-cy)*(v2[1]-cy)))))
