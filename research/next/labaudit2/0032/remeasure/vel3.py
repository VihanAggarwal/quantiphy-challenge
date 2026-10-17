import cv2,json,numpy as np
C=json.load(open('table_corners2.json'))
imgp=np.array([C['NL'],C['NR'],C['FR'],C['FL']],float)
obj=np.array([[0,0,0],[0.603,0,0],[0.603,0.760,0],[0,0.760,0]],float)
Ww=json.load(open('wrow.json')); Ws=json.load(open('wshadow.json'))
ks=np.arange(36,49); c=ks+2; t=c/25.
x=np.array([Ww[str(k)][1][0] for k in ks]); ysh=np.array([Ws[str(k)]['ysh'] for k in ks])
yc=np.array([Ww[str(k)][1][1] for k in ks]); d=np.array([2*Ww[str(k)][1][2] for k in ks])
def pose(f):
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    ok,rv,tv=cv2.solvePnP(obj,imgp,K,None,flags=cv2.SOLVEPNP_IPPE)
    R,_=cv2.Rodrigues(rv); n=R[:,2]; h=float(n@tv.ravel())  # plane: n.X = n.t  (points on table)
    return K,n,h
def backproj(f,n,h0,xs,ys):
    r=np.c_[(xs-640)/f,(ys-360)/f,np.ones_like(xs)]
    s=h0/(r@n); return s[:,None]*r
def speeds(P,label):
    i40,i41=2,3
    raw=np.linalg.norm(P[i41]-P[i40])*2500
    o=['raw40->41 %.1f'%raw]
    for lo,hi,deg in [(38,44,1),(38,46,2),(38,50,2),(38,50,1),(39,42,1)]:
        m=(c>=lo)&(c<=hi)
        V=np.array([np.polyval(np.polyder(np.polyfit(t[m],P[m,j],deg)),40.5/25) for j in range(3)])*100
        o.append('%d-%d/%d %.1f'%(lo,hi,deg,np.linalg.norm(V)))
    print('  ',label,' | '.join(o))
for f in [711,740,770,800]:
    K,n,h0=pose(f)
    # horizon y at x=735
    yh=360-(n[2]*f+n[0]*(735-640))/n[1]
    Pc=backproj(f,n,h0,x,ysh)   # contact (shadow line) points on table plane
    rng=np.linalg.norm(Pc,axis=1)
    # check vs ToF anchor: centre range at video36 = 1.373
    Pcent=Pc+0.02*(-n if n[1]>0 else n)  # move up by r (up = -y in cam ~); n sign check
    print('f=%d plane h=%.4f horizon@735=%.1f  n=%s  centre range@cap38=%.4f (ToF centre 1.373)'%(f,abs(h0),yh,n.round(4),np.linalg.norm(Pcent[0])))
    speeds(Pc,'shadow-plane (PnP scale)')
    # rescale so centre range at capture 38 matches ToF
    s=1.373/np.linalg.norm(Pcent[0])
    speeds(Pc*s,'shadow-plane (ToF-anchored, x%.3f)'%s)
    # size route with this f: Z=f*D/d
    Z=f*0.04/d; r=np.c_[(x-640)/f,(yc-360)/f,np.ones_like(x)]
    speeds(Z[:,None]*r,'size route (Z=fD/d)')
print()
f=770; K,n,h0=pose(f)
Pc=backproj(f,n,h0,x,ysh); Pcent=Pc-0.02*n*np.sign(n[1])*-1
Zs=f*0.04/d
for k,cc,zp,zs,P in zip(ks,c,Pc[:,2],Zs,Pc):
    print(k,cc,'Zplane %.4f Zsize %.4f ratio %.4f  X %.4f'%(zp,zs,zs/zp,P[0]))
dP=np.diff(Pc,axis=0)*2500
print('per-step speed (cm/s) cap38->50:',np.linalg.norm(dP,axis=1).round(1))
print('per-step vx:',dP[:,0].round(1)); print('per-step vz:',dP[:,2].round(1))
