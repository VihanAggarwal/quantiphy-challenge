import numpy as np, json
cx=640.;cy=360.;f=711.
Kinv=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1]]))
C=json.load(open('board_corners_o.json'))
def h(p): return np.array([p[0],p[1],1.])
print('frame  ownnormal: W(cm) L(cm) | jointnormal: W L   (scaled so centre range=2.815 at that frame)')
nj=np.load('n_fit_711.npy')[:3]
for k in ['30','31','33','34','36','37']:
    Q=np.array(C[k]); p=[h(q) for q in Q]
    v1=np.cross(np.cross(p[0],p[1]),np.cross(p[3],p[2])); v2=np.cross(np.cross(p[1],p[2]),np.cross(p[0],p[3]))
    d1=Kinv@v1; d2=Kinv@v2; n=np.cross(d1,d2); n/=np.linalg.norm(n); n=n if n[1]>0 else -n
    c=np.cross(np.cross(p[0],p[2]),np.cross(p[1],p[3]))
    out=[]
    for nn in (n,nj):
        X=np.array([(Kinv@q)/(nn@(Kinv@q)) for q in p]); Xc=(Kinv@c)/(nn@(Kinv@c))
        s=2.815/np.linalg.norm(Xc); X=X*s
        L=(np.linalg.norm(X[1]-X[0])+np.linalg.norm(X[2]-X[3]))/2; W=(np.linalg.norm(X[3]-X[0])+np.linalg.norm(X[2]-X[1]))/2
        out+= [W*100,L*100]
    print(k,np.round(out,1))
