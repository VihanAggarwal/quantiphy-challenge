import json, numpy as np
f=711.;cx=640.;cy=360.
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0035/rm2/track_ax.json'))
def cap(i): return int(np.floor(i*25/24+0.5))
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]);return d/np.linalg.norm(d)
def series(key,i0,i1):
    rows=[]
    for i in range(i0,i1+1):
        d=T[str(i)].get(key)
        if d: rows.append((cap(i),d['cxw'],d['cyw'],d['dsoft'],min(d['elax'])))
    return np.array(rows)
sb=series('sb',21,47); bb=series('bb',21,48)
Rs=0.095; Rb=0.116
# anchor sizes: video38 = capture 40
def anchor(S,j,rng_surface,R):
    k=np.where(S[:,0]==j)[0][0]
    # smooth size by linear fit over neighbourhood to reduce single-frame noise
    m=(abs(S[:,0]-j)<=8)
    p=np.polyfit(S[m,0],S[m,3],1); dj=np.polyval(p,j)
    return (rng_surface+R)*dj, dj
Ks,ds40=anchor(sb,40,3.052,Rs); Kb,db40=anchor(bb,40,2.412,Rb)
print('sb size@40 (lin fit) %.2f  K=%.3f; bb size@40 %.2f K=%.3f'%(ds40,Ks,db40,Kb))
print('implied diameters f=711: sb %.1f cm  bb %.1f cm'%(2*Ks/f*100*0.5*1, 2*Kb/f*100*0.5))
def traj(S,K):
    return np.array([ray(u,v)*(K/d) for _,u,v,d,_ in S])
Psb=traj(sb,Ks); Pbb=traj(bb,Kb)
def planefit(P):
    c=P.mean(0); u,s,vt=np.linalg.svd(P-c); n=vt[2]
    if n[1]>0: n=-n
    return n,c,s
for nm,P,S in (('sb',Psb,sb),('bb',Pbb,bb)):
    n,c,s=planefit(P); print(nm,'normal',np.round(n,3),'sing',np.round(s,3))
np.save('/home/user/quantiphy-challenge/research/next/labaudit2/0035/rm2/tmp_traj.npy',np.array([0]))

# ---- joint floor fit: n.P + c = R for ball centres ----

pts=[(p,Rs) for p in Psb]+[(p,Rb) for p in Pbb]
# ToF-anchored points at 0.6 s (capture 15 = video 14)
s14=T['14']['sb']; b14=T['14']['bb']
tof06=[(ray(s14['cxw'],s14['cyw'])*(2.758+Rs),Rs),(ray(b14['cxw'],b14['cyw'])*(2.270+Rb),Rb)]
def nvec(th,ph): return np.array([np.sin(th)*np.cos(ph),-np.cos(th),np.sin(th)*np.sin(ph)])
def fitplane(pts):
    P=np.array([p for p,_ in pts]); R=np.array([r for _,r in pts])
    best=None
    for th in np.radians(np.arange(0,90,0.25)):
        for ph in np.radians(np.arange(0,360,0.5)):
            n=nvec(th,ph); r=P@n-R; c=-r.mean(); e=np.sqrt(np.mean((r+c)**2))
            if best is None or e<best[0]: best=(e,th,ph,c)
    e,th,ph,c=best
    return nvec(th,ph),c,e
for nm,pp in (('traj only',pts),('traj+tof06',pts+tof06*5),('tof4 only',tof06+[(ray(T['38']['sb']['cxw'],T['38']['sb']['cyw'])*(3.052+Rs),Rs),(ray(T['38']['bb']['cxw'],T['38']['bb']['cyw'])*(2.412+Rb),Rb)])):
    n,c,rms=fitplane(pp)
    print(nm,'n',np.round(n,3),'cam height %.3f'%c,'rms %.3f'%rms,'pitch(deg below horiz of optical axis) %.1f'%np.degrees(np.arcsin(n[2])) )

print('\n==== Route 1: ray / floor-plane intersection ====')
planes={}
for nm,pp in (('traj only',pts),('traj+tof06',pts+tof06*5),('tof4',tof06+[(ray(T['38']['sb']['cxw'],T['38']['sb']['cyw'])*(3.052+Rs),Rs),(ray(T['38']['bb']['cxw'],T['38']['bb']['cyw'])*(2.412+Rb),Rb)])):
    planes[nm]=fitplane(pp)[:2]
sbfull=series('sb',21,47)
J=sbfull[:,0]
def onplane(S,n,c,R):
    out=[]
    for _,u,v,_,_ in S:
        r=ray(u,v); t=(R-c)/(n@r); out.append(r*t)
    return np.array(out)
def smooth_vel(J,P,j0,half=6,deg=2):
    m=(J>=j0-half)&(J<=j0+1+half)
    tt=(J[m]-(j0+0.5))/25.
    co=[np.polyfit(tt,P[m,k],deg) for k in range(3)]
    v=np.array([np.polyval(np.polyder(c),0) for c in co])  # velocity at t=j0+0.5 (midpoint of forward diff)
    fd=np.array([ (np.polyval(c,0.5/25)-np.polyval(c,-0.5/25))*25 for c in co])
    return v,fd
for nm,(n,c) in planes.items():
    P=onplane(sbfull,n,c,Rs)
    k40=np.where(J==40)[0][0]; k41=np.where(J==41)[0][0]
    raw=np.linalg.norm(P[k41]-P[k40])*25
    rng40=np.linalg.norm(P[k40])
    out=[]
    for half,deg in ((4,1),(6,2),(8,2),(10,2)):
        v,fd=smooth_vel(J,P,40,half,deg); out.append('h%d d%d: %.1f'%(half,deg,np.linalg.norm(fd)*100))
    print('%-11s range@40 centre %.3f (ToF surf+R=%.3f) | raw FD40->41 %.1f cm/s | smoothed: %s'%(nm,rng40,3.052+Rs,raw*100,'; '.join(out)))
    k14=None
print('\n==== Route 2: size-based depth ====')
P=Psb; J2=sb[:,0]
k40=np.where(J2==40)[0][0]; k41=np.where(J2==41)[0][0]
print('raw FD 40->41 %.1f cm/s'%(np.linalg.norm(P[k41]-P[k40])*2500))
for half,deg in ((4,1),(6,1),(6,2),(8,2),(10,2),(12,2)):
    v,fd=smooth_vel(J2,P,40,half,deg)
    print(' h%d d%d |v|=%.1f cm/s  comps(cm/s) %s  range-rate %.1f'%(half,deg,np.linalg.norm(fd)*100,np.round(fd*100,1), (fd@ray(T['38']['sb']['cxw'],T['38']['sb']['cyw']))*100))

print('\n==== per-frame range: plane (traj+tof06) vs size ====')
n,c=planes['traj+tof06']
Pp=onplane(sbfull,n,c,Rs)
bbfull=series('bb',21,48); Pbp=onplane(bbfull,n,c,Rb)
for k in range(len(sbfull)):
    j=int(sbfull[k,0])
    kb=np.where(bbfull[:,0]==j)[0]
    sbs='SB j%2d u%6.1f v%6.1f d%5.1f  rng plane %.3f size %.3f'%(j,sbfull[k,1],sbfull[k,2],sbfull[k,3],np.linalg.norm(Pp[k]),np.linalg.norm(Psb[k]))
    if len(kb):
        kb=kb[0]; sbs+=' | BB d%5.1f plane %.3f size %.3f'%(bbfull[kb,3],np.linalg.norm(Pbp[kb]),np.linalg.norm(Pbb[kb]))
    print(sbs)

print('\n==== linear fits over the uniform-motion segment (capture 31..49) ====')
def linvel(J,P,j0=31,j1=49):
    m=(J>=j0)&(J<=j1); tt=J[m]/25.
    v=np.array([np.polyfit(tt,P[m,k],1)[0] for k in range(3)])
    return v
r40=ray(T['38']['sb']['cxw'],T['38']['sb']['cyw'])
for nm,(n,c) in planes.items():
    P=onplane(sbfull,n,c,Rs); v=linvel(J,P)
    lat=v-(v@r40)*r40
    print('plane %-11s |v|=%.1f  lateral %.1f range-rate %.1f'%(nm,np.linalg.norm(v)*100,np.linalg.norm(lat)*100,(v@r40)*100))
v=linvel(J2,Psb); lat=v-(v@r40)*r40
print('size route        |v|=%.1f  lateral %.1f range-rate %.1f'%(np.linalg.norm(v)*100,np.linalg.norm(lat)*100,(v@r40)*100))
for a,b in ((33,47),(35,45),(36,46),(31,45)):
    v=linvel(J2,Psb,a,b); print('  size route j%d-%d |v|=%.1f range-rate %.1f'%(a,b,np.linalg.norm(v)*100,(v@r40)*100))
    n,c=planes['traj+tof06']; v=linvel(J,onplane(sbfull,n,c,Rs),a,b); print('  plane      j%d-%d |v|=%.1f range-rate %.1f'%(a,b,np.linalg.norm(v)*100,(v@r40)*100))
# check traj-only plane vs ToF at 0.6 s (capture 15 = video 14)
s14=T['14']['sb']
for nm,(n,c) in planes.items():
    r=ray(s14['cxw'],s14['cyw']); t=(Rs-c)/(n@r)
    print('0.6s check %-11s plane centre range %.3f vs ToF surf+R %.3f'%(nm,t,2.758+Rs))

print('\n==== measured soccer size vs plane-predicted size (K from j40 ToF anchor) ====')
n,c=planes['traj+tof06']; Pp=onplane(sbfull,n,c,Rs)
rp=np.linalg.norm(Pp,axis=1)
dpred=Ks/rp
for k in range(len(sbfull)):
    print('j%2d meas deq %.2f  minor %.2f  pred %.2f  diff %+.2f'%(sbfull[k,0],sbfull[k,3],sbfull[k,4],dpred[k],sbfull[k,3]-dpred[k]))
# best-fit: is measured size better explained by a plane with different tilt? regress log d on log rho_plane
m=sbfull[:,0]>=27
b=np.polyfit(np.log(rp[m]),np.log(sbfull[m,3]),1)
print('log-log slope (expect -1): %.3f'%b[0])
