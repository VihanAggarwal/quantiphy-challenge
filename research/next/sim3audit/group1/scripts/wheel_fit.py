import numpy as np, cv2
out=np.load('scripts/rim_edges.npy')
cx0, cy0 = 1731.5, 1164.3
def fit(pts):
    P=pts.astype(np.float32)
    (ex,ey),(a,b),ang=cv2.fitEllipse(P)
    return ex,ey,a,b,ang
spokes = np.array([90+36*k for k in range(10)])%360
def nearspoke(a, tol=7):
    d=np.abs(((a-spokes)+180)%360-180); return d.min()<tol
for name, col_r, col_g, thr, sign in [('outer',3,4,6,1),('inner',1,2,-5,-1)]:
    sel=[]
    for row in out:
        a=row[0]; r=row[col_r]; gval=row[col_g]
        if (gval*sign) > abs(thr) and not nearspoke(a):
            t=np.deg2rad(a); sel.append((cx0+r*np.cos(t), cy0+r*np.sin(t), a))
    sel=np.array(sel)
    ex,ey,A,B,ang=fit(sel[:,:2])
    print(name, 'n=%d'%len(sel), 'angles covered:', np.unique((sel[:,2]//30*30).astype(int)))
    print('   centre (%.2f, %.2f) full axes %.2f x %.2f  angle %.1f  -> minor/major %.4f'%(ex,ey,A,B,ang,min(A,B)/max(A,B)))
print('--- axis-aligned / small tilt ellipse fits (geometric-ish residual)')
def fit_aa(P, tilt=False):
    ex,ey=P[:,0].mean(),P[:,1].mean(); a=b=np.sqrt(((P-[ex,ey])**2).sum(1)).mean(); th=0.0
    p=np.array([ex,ey,a,b,th])
    for it in range(50):
        ex,ey,a,b,th=p
        def resid(p):
            ex,ey,a,b,th=p
            dx=P[:,0]-ex; dy=P[:,1]-ey
            u=dx*np.cos(th)+dy*np.sin(th); v=-dx*np.sin(th)+dy*np.cos(th)
            return (np.sqrt((u/a)**2+(v/b)**2)-1)*np.sqrt(a*b)
        r=resid(p); J=[]
        for k in range(5 if tilt else 4):
            dp=np.zeros(5); dp[k]=1e-4 if k==4 else 1e-3
            J.append((resid(p+dp)-r)/dp[k])
        J=np.array(J).T
        step=np.linalg.lstsq(J,-r,rcond=None)[0]
        p[:len(step)]+=step
    return p, np.sqrt((resid(p)**2).mean())
for name, col_r, col_g, thr, sign in [('outer',3,4,6,1),('inner',1,2,-5,-1)]:
    sel=[]
    for row in out:
        a=row[0]; r=row[col_r]; gval=row[col_g]
        if (gval*sign) > abs(thr) and not nearspoke(a):
            t=np.deg2rad(a); sel.append((cx0+r*np.cos(t), cy0+r*np.sin(t)))
    sel=np.array(sel)
    for tilt in (False,True):
        p,rms=fit_aa(sel,tilt)
        print(name,'tilt' if tilt else 'aa  ','centre (%.2f,%.2f) a=%.2f b=%.2f th=%.2fdeg  aspect a/b=%.4f rms=%.2f'%(p[0],p[1],p[2],p[3],np.degrees(p[4]),p[2]/p[3],rms))
print('--- with radius gating')
for name, col_r, col_g, thr, sign, rlo, rhi in [('outer',3,4,4,1,94,107),('inner',1,2,-4,-1,78,95)]:
    sel=[]; angs=[]
    for row in out:
        a=row[0]; r=row[col_r]; gval=row[col_g]
        if (gval*sign) > abs(thr) and not nearspoke(a) and rlo<r<rhi:
            t=np.deg2rad(a); sel.append((cx0+r*np.cos(t), cy0+r*np.sin(t))); angs.append(a)
    sel=np.array(sel); angs=np.array(angs)
    print(name,'n',len(sel),'angle bins',np.unique((angs//30*30).astype(int)))
    P=sel
    for it in range(3):
        p,rms=fit_aa(P,False)
        dx=P[:,0]-p[0]; dy=P[:,1]-p[1]; rr=(np.sqrt((dx/p[2])**2+(dy/p[3])**2)-1)*np.sqrt(p[2]*p[3])
        print('   it',it,'centre (%.2f,%.2f) a=%.2f b=%.2f aspect=%.4f rms=%.2f n=%d'%(p[0],p[1],p[2],p[3],p[2]/p[3],rms,len(P)))
        P=P[np.abs(rr)<2.5*rms]
