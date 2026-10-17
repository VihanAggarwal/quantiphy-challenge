# Rolling-phase (capture 38..50 = video 36..48) speed of the white ball by fits, two depth routes:
#  P: plane route (centre ray at h-r; centre = edge-midpoint or threshold centroid); h from stated 1.353 at c38
#  S: size route with the exact sphere silhouette (sil.py): measured width w_k = k*w_sil(Z) (proportional) or
#     w_sil(Z)+e (additive); calibration constant from the stated range at c38 applied through a straight-line fit
#     of the size-derived Z over the window. Speed = |velocity| of a linear (or quadratic) LSQ fit of 3D points.
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
from geo import plane, X_on
from sil import extents
def brentq(g,a,b,tol=1e-7):
    ga,gb=g(a),g(b)
    assert ga*gb<0,(a,b,ga,gb)
    for _ in range(100):
        m=0.5*(a+b); gm=g(m)
        if ga*gm<=0: b,gb=m,gm
        else: a,ga=m,gm
        if b-a<tol: break
    return 0.5*(a+b)
TB=json.load(open(D+'topbot.json')); T=json.load(open(D+'track.json'))
f=float(sys.argv[1]) if len(sys.argv)>1 else 711.
n,Ki,_=plane(f)
r_b=0.02; RS=1.353; A=36
def rayu(p): r=Ki@np.array([p[0],p[1],1.]); return r/np.linalg.norm(r)
def fitv(P,ks,deg=1,tq=None):
    t=np.array([cap(k)/25. for k in ks]); X=np.array([P[k] for k in ks])
    if tq is None: tq=cap(A)/25.
    c=np.polyfit(t-tq,X,deg); return c
res=[]
for rr in ['x','o']:
    for cname in ['edge','centroid']:
        U={}
        for k in range(33,49):
            q=TB[rr][str(k)]
            U[k]=np.array([(q['left']+q['right'])/2,(q['top']+q['bot'])/2]) if cname=='edge' else np.array([T[rr][str(k)]['wht']['cx'],T[rr][str(k)]['wht']['cy']])
        W={k:TB[rr][str(k)]['right']-TB[rr][str(k)]['left'] for k in range(33,49)}
        # plane route
        Xu={k:X_on(U[k],n,Ki,1.0) for k in U}; s=(RS+r_b)/np.linalg.norm(Xu[A]); PP={k:Xu[k]*s for k in U}
        tracks={'P':PP}
        # size routes: for each frame, function Z -> silhouette width along ray U[k]
        def wsil(k,Z):
            u=rayu(U[k]); C=u*(Z/u[2]); return extents(C,r_b,f)[0]
        for model in ['prop','add']:
            # unknown calibration c: prop: w=c*wsil ; add: w=wsil+c. choose c so that the linear fit of R over
            # frames 36..48 passes through RS+r_b at c38
            def Zs(c):
                out={}
                for k in range(36,49):
                    g=(lambda Z: c*wsil(k,Z)-W[k]) if model=='prop' else (lambda Z: wsil(k,Z)+c-W[k])
                    out[k]=brentq(g,0.5,3.0)
                return out
            def resid(c):
                Z=Zs(c); ks=sorted(Z); t=np.array([cap(k) for k in ks]); R=np.array([Z[k]*np.linalg.norm(rayu(U[k])/rayu(U[k])[2]) for k in ks])
                p=np.polyfit(t-cap(A),R,1); return p[1]-(RS+r_b)
            c=brentq(resid,0.8,1.3) if model=='prop' else brentq(resid,-3,5)
            Z=Zs(c); PS={k:rayu(U[k])*(Z[k]/rayu(U[k])[2]) for k in Z}
            tracks['S'+model+'(c=%.3f)'%c]=PS
        for tn,P in tracks.items():
            ks=[k for k in range(36,49)]
            c1=fitv(P,ks,1); c2=fitv(P,ks,2)
            v1=100*np.linalg.norm(c1[0]); v2=100*np.linalg.norm(c2[1]); a2=2*c2[0]
            # FD c38->c39 on the quadratic fit
            fd2=100*np.linalg.norm(np.polyval(c2,0.04)-np.polyval(c2,0.0))/0.04
            fd2b=100*np.linalg.norm(np.polyval(c2,0.08)-np.polyval(c2,0.04))/0.04   # c39->c40
            k6=[k for k in range(36,43)]; c6=fitv(P,k6,1)
            res.append((rr,cname,tn,v1,v2,fd2,fd2b,100*np.linalg.norm(c6[0])))
print('f=%.0f'%f)
print('%-4s %-9s %-16s %8s %8s %9s %9s %9s'%('rnd','centre','route','lin36-48','quad@c38','FDq38-39','FDq39-40','lin36-42'))
for r in res: print('%-4s %-9s %-16s %8.1f %8.1f %9.1f %9.1f %9.1f'%r)
