# Sphere-silhouette fit to radial edge points (o render, sharp frames). Model: projected sphere ellipse
# (pinhole f=711): params = image centre of ellipse (u,v) and tangential semi-axis b; a/b set by off-axis angle.
import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0016/scripts'); from lm import least_squares
FR='/home/user/quantiphy-challenge/research/next/labaudit/0016/frames/f%s_%02d.png'
f=711.; pp=np.array([640.,360.])
def edges(gray,c,angs,r0,r1,pol=-1):
    pts=[]
    for a in angs:
        d=np.array([np.cos(a),np.sin(a)]); rs=np.arange(r0,r1,0.25)
        xy=c[None]+rs[:,None]*d[None]
        v=cv2.remap(gray,xy[:,0].astype(np.float32).reshape(1,-1),xy[:,1].astype(np.float32).reshape(1,-1),cv2.INTER_LINEAR)[0]
        v=cv2.GaussianBlur(v.reshape(1,-1).astype(np.float32),(1,5),1.0).ravel() if False else v
        gd=np.gradient(v)*pol
        k=np.argmax(gd)
        if 1<=k<len(rs)-1:
            y0,y1,y2=gd[k-1],gd[k],gd[k+1]; den=y0-2*y1+y2; off=0.5*(y0-y2)/den if den!=0 else 0
            pts.append(xy[k]+off*0.25*d)
    return np.array(pts)
def ellipse_pts_resid(p,pts):
    u,v,b=p; c=np.array([u,v]); x=c-pp; rr=np.hypot(*x); th=np.arctan(rr/f)
    ur=x/rr; ut=np.array([-ur[1],ur[0]])
    # a/b for small alpha ~ 1/cos(th) (exact: a/b = sqrt(1-s^2)/sqrt(cos^2-s^2) ~ 1/cos)
    a=b/np.cos(th)
    q=pts-c; X=q@ur; Y=q@ut
    rho=np.sqrt((X/a)**2+(Y/b)**2)
    return (rho-1)*np.sqrt((X**2+Y**2))  # approx px distance
def fit(pts,c0,b0):
    s=least_squares(lambda p: ellipse_pts_resid(p,pts),np.r_[c0,b0]); return s
if __name__=='__main__':
    rend=sys.argv[1]; fr=int(sys.argv[2]); c0=np.array([float(sys.argv[3]),float(sys.argv[4])])
    sectors=[tuple(map(float,s.split(':'))) for s in sys.argv[5].split(',')]
    im=cv2.imread(FR%(rend,fr)); gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
    angs=np.concatenate([np.radians(np.arange(a0,a1,3)) for a0,a1 in sectors])
    pts=edges(gray,c0,angs,float(sys.argv[6]) if len(sys.argv)>6 else 25,float(sys.argv[7]) if len(sys.argv)>7 else 70)
    s=fit(pts,c0,45.)
    r=s.fun; keep=np.abs(r)<2.5*np.median(np.abs(r))+0.5
    s=fit(pts[keep],s.x[:2],s.x[2])
    u,v,b=s.x; x=np.array([u,v])-pp; th=np.arctan(np.hypot(*x)/f)
    print('frame %d %s: centre (%.1f,%.1f) b=%.2f (tangential diam %.1f px) th=%.1f deg  n=%d rms=%.2f px'%(fr,rend,u,v,b,2*b,np.degrees(th),keep.sum(),np.sqrt(np.mean(s.fun**2))))
    # range (centre) for D: b = f s/sqrt(cos^2-s^2), s=R/d
    for D in [0.170,0.177,0.184,0.19]:
        R=D/2; s_=b*np.cos(th)/np.sqrt(f*f+b*b); d=R/s_
        print('   D=%.3f: centre range %.3f surface %.3f'%(D,d,d-R))
    np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/edge_%s_%d.npy'%(rend,fr),pts[keep])
