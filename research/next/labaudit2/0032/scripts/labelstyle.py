# Label-style forward differences for the motion rows (deterministic, no noise):
#   P_n = d_n * ray(click_n); speed = |P_{n+1}-P_n| * 25.  d at the stated time = stated range; d at the next frame =
#   stated + Delta(surface range) from a depth model (plane route raw / plane fit / size fit). Clicks = measured centres.
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
from geo import plane, X_on
TB=json.load(open(D+'topbot.json')); T=json.load(open(D+'track.json'))
f=float(sys.argv[1]) if len(sys.argv)>1 else 711.
n,Ki,_=plane(f)
def rayu(p,f=f): r=np.array([(p[0]-640)/f,(p[1]-360)/f,1.]); return r/np.linalg.norm(r)
def click(rr,key,k,mode):
    if key=='wht' and mode=='edge':
        q=TB[rr][str(k)]; return np.array([(q['left']+q['right'])/2,(q['top']+q['bot'])/2])
    t=T[rr][str(k)][key]; return np.array([t['cx'],t['cy']])
def planeR(rr,key,k,mode,rad):
    return np.linalg.norm(X_on(click(rr,key,k,mode),n,Ki,1.0))
def lab(rr,key,rad,dstat,k0,k1,mode,dR=None,c0=None):
    # c0: optional click override for frame k0 (interpolated dropped frame)
    u0=click(rr,key,k0,mode) if c0 is None else c0; u1=click(rr,key,k1,mode)
    if dR is None:   # plane raw ratio
        s=(dstat+rad)/np.linalg.norm(X_on(u0,n,Ki,1.0)); d1=np.linalg.norm(X_on(u1,n,Ki,1.0))*s-rad
    else: d1=dstat+dR
    P0=dstat*rayu(u0); P1=d1*rayu(u1); dc=1
    V=(P1-P0)*25; r0=P0/np.linalg.norm(P0)
    return 100*np.linalg.norm(V), 100*(V@r0), 100*np.linalg.norm(V-(V@r0)*r0)
print('f=%.0f'%f)
for rr in ['x','o']:
  for mode in ['edge','centroid']:
    # white ball, t=1.5 as c38 (video 36) -> c39 (video 37)
    a=lab(rr,'wht',0.02,1.353,36,37,mode)
    b=lab(rr,'wht',0.02,1.353,36,37,mode,dR=-0.615/25*1.0)   # plane-fit radial ~ -61.5 cm/s
    c=lab(rr,'wht',0.02,1.353,36,37,mode,dR=-0.70/25)        # size-route-like radial ~ -70 cm/s
    # white ball t=1.5 as c37 (dropped; click interpolated between video 35 and 36) -> c38 (video 36)
    cm=(click(rr,'wht',35,mode)+click(rr,'wht',36,mode))/2
    d=lab(rr,'wht',0.02,1.353,36,36,mode,c0=cm)  # plane raw ratio between interpolated c37 and v36
    # white ball t=1.6 = c40 (video 38) -> c41 (video 39); stated range unknown: anchor via plane (scale from c38)
    s=(1.353+0.02)/planeR(rr,'wht',36,mode,0.02); d40=planeR(rr,'wht',38,mode,0.02)*s-0.02
    e=lab(rr,'wht',0.02,d40,38,39,mode); e2=lab(rr,'wht',0.02,d40,38,39,mode,dR=-0.615/25)
    print('%s %-8s white v1.5 c38->39: plane-raw %.1f (rad %.1f lat %.1f) | plane-fit dR %.1f | size-like dR %.1f || c37->38 plane-raw %.1f (rad %.1f lat %.1f) || v1.6 c40->41 plane-raw %.1f, fit-dR %.1f (d40=%.3f)'%(rr,mode,a[0],a[1],a[2],b[0],c[0],d[0],d[1],d[2],e[0],e2[0],d40))
  # tennis ball t=1.5: c38->c39 (video 36->37) and c37->c38
  for mode in ['centroid']:
    a=lab(rr,'yel',0.0335,1.183,36,37,mode)
    cm=(click(rr,'yel',35,mode)+click(rr,'yel',36,mode))/2
    d=lab(rr,'yel',0.0335,1.183,36,36,mode,c0=cm)
    print('%s tennis v1.5 c38->39 plane-raw %.1f (rad %.1f lat %.1f) || c37->38 %.1f (rad %.1f lat %.1f)'%(rr,a[0],a[1],a[2],d[0],d[1],d[2]))
