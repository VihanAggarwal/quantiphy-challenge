import numpy as np, cv2
cx=640.;cy=360.
C=np.load('c29_table_corners.npy')  # FL,FR,BR,BL
def h(p): return np.array([p[0],p[1],1.])
for f in [700.,711.,722.]:
    Kinv=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1]]))
    p=[h(q) for q in C]
    v1=np.cross(np.cross(p[0],p[1]),np.cross(p[3],p[2])); v2=np.cross(np.cross(p[1],p[2]),np.cross(p[0],p[3]))
    d1=Kinv@v1; d2=Kinv@v2; d1/=np.linalg.norm(d1); d2/=np.linalg.norm(d2)
    n=np.cross(d1,d2); n/=np.linalg.norm(n); n=n if n[1]>0 else -n
    X=np.array([(Kinv@q)/(n@(Kinv@q)) for q in p])
    s=[np.linalg.norm(X[(k+1)%4]-X[k]) for k in range(4)]
    # scale so front edge = 76.0 cm, also check depth edges vs 60.3
    sc=0.760/((s[0]+s[2])/2)
    print('f',f,'cos',round(abs(d1@d2),3),'aspect front/side',round((s[0]+s[2])/(s[1]+s[3]),4),'(76/60.3=%.4f)'%(76/60.3),'scale(h of table plane)',round(sc,4),'side cm',round((s[1]+s[3])/2*sc*100,1))
