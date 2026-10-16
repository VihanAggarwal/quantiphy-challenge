import numpy as np
FL,FR,BR=np.load('scripts/table_pts.npy')
front,right,back,left=np.load('scripts/table_lines.npy')
cx,cy=640.,360.
def geo(f, width=0.603):
    K=np.array([[f,0,cx],[0,f,cy],[0,0,1.]])
    v1=np.cross(left,right); v1=v1/v1[2]
    d1=np.linalg.solve(K,v1); d1/=np.linalg.norm(d1)
    nF=K.T@front; d2=np.cross(nF,d1); d2/=np.linalg.norm(d2)
    n=np.cross(d1,d2); n/=np.linalg.norm(n)
    ray=lambda p: np.linalg.solve(K,[p[0],p[1],1.])
    P=lambda p,h=1.0: ray(p)*h/(n@ray(p))
    w=np.linalg.norm(P(FR)-P(FL)); h=width/w
    return K,n,h,ray
def on_plane(p,f=711,off=0.0):
    K,n,h,ray=geo(f); r=ray(p); return r*(h-off)/(n@r)
if __name__=='__main__':
    for f in [711,730]:
        K,n,h,ray=geo(f)
        print('f',f,'n',n,'h',h)
        for nm,p,off in [('f41 ball centre',(605,491),0.03),('f39 ball centre',(610.6,461),0.03),('f40',(607.4,469),0.03),('front edge mid',(610,488),0.0)]:
            X=on_plane(p,f,off); print('  ',nm,'range %.3f'%np.linalg.norm(X))
