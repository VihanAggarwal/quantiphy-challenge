import numpy as np, json
C=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0033/corners.json'))
P=np.array([C['FL'],C['FR'],C['NR'],C['NL']])
F=711.; CX=640.; CY=360.
def ray(u,v): return np.array([(u-CX)/F,(v-CY)/F,1.0])
def table_plane(W=60.3,D=76.0,mode='avg'):
    d=np.array([ray(*p) for p in P])
    A=np.c_[-d[2],d[1],d[3]]; b=d[0]
    sol,*_=np.linalg.lstsq(A,b,rcond=None)
    lam=np.r_[1,sol[1],sol[0],sol[2]]
    X=d*lam[:,None]
    w=(np.linalg.norm(X[1]-X[0])+np.linalg.norm(X[2]-X[3]))/2; dd=(np.linalg.norm(X[3]-X[0])+np.linalg.norm(X[2]-X[1]))/2
    s={'W':W/w,'D':D/dd,'avg':0.5*(W/w+D/dd),'area':np.sqrt(W*D/(w*dd))}[mode]
    X=X*s
    n=np.cross(X[1]-X[0],X[3]-X[0]); n/=np.linalg.norm(n)
    if n[1]>0: n=-n   # up normal points toward -y (image up)
    c=X.mean(0); h=-np.dot(n,c)  # plane: n.x + h =0 ; camera height above plane = h
    return X,n,h
if __name__=='__main__':
    for mode in ['W','D','avg']:
        X,n,h=table_plane(mode=mode)
        print(mode,'corners range',np.round(np.linalg.norm(X,axis=1),1),'n',np.round(n,3),'cam height above table %.1f cm'%h,
              'pitch %.1f deg'%np.degrees(np.arcsin(-n[2])))
