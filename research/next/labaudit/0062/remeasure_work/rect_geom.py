import numpy as np, json
cx=640.; cy=360.
C=json.load(open('board_corners_o.json'))
def h(p): return np.array([p[0],p[1],1.])
def analyze(Q,f):
    Kinv=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1]]))
    p=[h(q) for q in Q]
    # sides: 0-1 (far long edge), 1-2 (right), 2-3 (near), 3-0 (left)
    v1=np.cross(np.cross(p[0],p[1]),np.cross(p[3],p[2]))
    v2=np.cross(np.cross(p[1],p[2]),np.cross(p[0],p[3]))
    d1=Kinv@v1; d2=Kinv@v2; d1/=np.linalg.norm(d1); d2/=np.linalg.norm(d2)
    cosang=abs(d1@d2)
    n=np.cross(d1,d2); n/=np.linalg.norm(n)
    if n[1]<0: n=-n
    # back-project corners to plane n.X=1
    X=[]
    for q in p:
        r=Kinv@q; X.append(r/(n@r))
    X=np.array(X)
    s=[np.linalg.norm(X[(k+1)%4]-X[k]) for k in range(4)]
    return cosang,n,s,X
# f that makes rectangle orthogonal: solve per frame
def f_ortho(Q):
    p=[h(q) for q in Q]
    v1=np.cross(np.cross(p[0],p[1]),np.cross(p[3],p[2])); v2=np.cross(np.cross(p[1],p[2]),np.cross(p[0],p[3]))
    v1=v1/v1[2]; v2=v2/v2[2]
    val=-((v1[0]-cx)*(v2[0]-cx)+(v1[1]-cy)*(v2[1]-cy))
    return np.sqrt(val) if val>0 else np.nan
for i,Q in sorted(C.items(),key=lambda x:int(x[0])):
    ca,n,s,X=analyze(Q,711.)
    tilt=np.degrees(np.arccos(n[1]))
    print(i,'cos',round(ca,3),'f_ortho',round(f_ortho(Q),0),'n',np.round(n,3),'sides/h',np.round(s,3),'aspect long/short',round((s[0]+s[2])/(s[1]+s[3]),3))
