# White ball 3D track on the capture clock by two depth routes, anchored to the stated surface range 1.353 at t=1.5
#   P (plane): centre ray hits the plane (h - r); h solved so that surface range at the anchor frame = 1.353
#   S (size):  Z ~ 1/size (equator width w, or top-bottom height); centre range = Z * |ray|/ray_z; anchored likewise
# centre pixel = (equator mid-x, (top+bot)/2) from topbot.json ; also the threshold centroid from track.json
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
from geo import plane, X_on
TB=json.load(open(D+'topbot.json')); T=json.load(open(D+'track.json'))
f=float(sys.argv[1]) if len(sys.argv)>1 else 711.
anchor=int(sys.argv[2]) if len(sys.argv)>2 else 36     # video frame of t=1.5 (36 -> c38)
n,Ki,_=plane(f)
def rayu(p): r=Ki@np.array([p[0],p[1],1.]); return r/np.linalg.norm(r)
r_b=0.02; RS=1.353
ks=list(range(33,49)); tc=np.array([cap(k) for k in ks],float)
out={}
for rr in ['x','o']:
    uv={}; size_w={}; size_h={}
    for k in ks:
        q=TB[rr][str(k)]; uv[k]=np.array([(q['left']+q['right'])/2,(q['top']+q['bot'])/2])
        size_w[k]=q['right']-q['left']; size_h[k]=q['bot']-q['top']
    uvc={k:np.array([T[rr if rr!='o' else 'o'][str(k)]['wht']['cx'],T[rr][str(k)]['wht']['cy']]) for k in ks}
    for cname,U in [('edge',uv),('centroid',uvc)]:
        # plane route
        Xu={k:X_on(U[k],n,Ki,1.0) for k in ks}
        s=(RS+r_b)/np.linalg.norm(Xu[anchor])
        PP={k:Xu[k]*s for k in ks}
        out[(rr,cname,'P')]=PP
        for sname,S in [('w',size_w),('h',size_h)]:
            # Z ~ 1/size; centre range at anchor = RS + r
            u=rayu(U[anchor]); Z0=(RS+r_b)*u[2]
            PS={}
            for k in ks:
                Z=Z0*S[anchor]/S[k]; uk=rayu(U[k]); PS[k]=uk*(Z/uk[2])
            out[(rr,cname,'S'+sname)]=PS
def fd(P,a,b): return 100*np.linalg.norm(P[b]-P[a])/((cap(b)-cap(a))/25.)
def linfit(P,k0,k1):
    kk=[k for k in ks if k0<=k<=k1]; t=np.array([cap(k)/25. for k in kk]); X=np.array([P[k] for k in kk])
    c=np.polyfit(t,X,1); return 100*np.linalg.norm(c[0])
def quadfit(P,k0,k1,tq):
    kk=[k for k in ks if k0<=k<=k1]; t=np.array([cap(k)/25. for k in kk])-tq; X=np.array([P[k] for k in kk])
    c=np.polyfit(t,X,2); return 100*np.linalg.norm(c[1]), c
print('f=%.0f anchor video %d (c%d)'%(f,anchor,cap(anchor)))
print('%-22s %7s %7s %7s %7s %7s | %8s %8s %8s %8s'%('track','c36-38','c38-39','c39-40','c40-41','c41-42','lin38-50','lin38-44','lin36-44','surf@c50'))
for key,P in out.items():
    print('%-22s %7.1f %7.1f %7.1f %7.1f %7.1f | %8.1f %8.1f %8.1f %8.3f'%('/'.join(key),fd(P,35,36),fd(P,36,37),fd(P,37,38),fd(P,38,39),fd(P,39,40),linfit(P,36,48),linfit(P,36,42),linfit(P,35,42),np.linalg.norm(P[48])-r_b))
import pickle; pickle.dump({k:{kk:v.tolist() for kk,v in P.items()} for k,P in out.items()},open(D+'white3d_f%d_a%d.pkl'%(f,anchor),'wb'))
