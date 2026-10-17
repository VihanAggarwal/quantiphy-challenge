import cv2, numpy as np, json, sys
tag = sys.argv[1] if len(sys.argv)>1 else 'a'
f = float(sys.argv[2]) if len(sys.argv)>2 else 775.0
E=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/edge_%s.json'%tag))
def cap(k): return k if k<=11 else (k+1 if k<=35 else k+2)
cx0,cy0=640.,360.
Rb={'t':3.35,'w':2.0}
P=np.load('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/corners.npy')
W,D=60.3,76.0
obj=np.array([[-W/2,D,0],[W/2,D,0],[W/2,0,0],[-W/2,0,0]],float)
K=np.array([[f,0,cx0],[0,f,cy0],[0,0,1]])
ok,rv,tv=cv2.solvePnP(obj,P,K,None,flags=cv2.SOLVEPNP_IPPE)
Rm,_=cv2.Rodrigues(rv); campos=(-Rm.T@tv).ravel()
def ray(u,v):
    d=np.array([(u-cx0)/f,(v-cy0)/f,1.0]); return d/np.linalg.norm(d)
res={}
for b in 't','w':
    rows=[]
    for o in E:
        if b not in o: continue
        u,v,r=o[b][0],o[b][1],o[b][2]
        d=ray(u,v); cth=d[2]
        # sphere image: semi-minor b=f sin a / sqrt(cos^2th - sin^2a), semi-major a=f sin a cos a/(cos^2th-sin^2a); use geometric mean ~ r
        # solve for sin a numerically
        sa=np.sin(np.arctan(r/f))
        for _ in range(20):
            ca=np.sqrt(1-sa*sa); den=cth*cth-sa*sa
            bb=f*sa/np.sqrt(den); aa=f*sa*ca/den
            g=np.sqrt(aa*bb)
            sa*= r/g
        Rc=Rb[b]/sa
        # ground-plane route: center on plane z=Rb in table frame
        dw=Rm.T@d  # ray dir in table frame
        s=(Rb[b]-campos[2])/dw[2]
        Rg=s
        rows.append((o['i'],cap(o['i']),u,v,r,Rc,Rg))
    res[b]=np.array(rows)
np.save('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/motion_%s_%d.npy'%(tag,int(f)),res,allow_pickle=True)
print('f',f,'campos',campos.round(2))
for b in 't','w':
    print(b)
    for row in res[b]:
        if row[0]>=14: print('  k=%2d c=%2d u=%.1f v=%.1f r=%.2f Rc_size=%.1f Rc_ground=%.1f'%tuple(row))
