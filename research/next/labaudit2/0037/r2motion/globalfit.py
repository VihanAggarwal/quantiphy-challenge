"""Global piecewise-ballistic 3D fit of the bouncing ping-pong ball (arcs B..E).
Camera: f=711, principal point (640,360); gravity direction from pitch/roll params.
Bounce: centre reaches plane n.P = Hc (Hc = camera-to-table distance minus ball radius).
Arc i between bounce times T[i], T[i+1]; vertical motion fixed by those times; horizontal
velocity per arc (2 params), position continuous at bounces."""
import json,sys,numpy as np
from lm import least_squares
f=711.0; CX,CY=640.,360.; g=9.81
def cap(n): return int(np.floor(25*n/24+0.5))
tr=json.load(open('tracks.json')); wd=json.load(open('widths.json'))
src=sys.argv[1] if len(sys.argv)>1 else 's'
shared=('shared' in sys.argv)
use=[21,22,23,24,25,26,27,30,31,32,33,34,37,38,39,40,41,42,44,45,46,47,48]
if 'with35' in sys.argv: use=sorted(use+[35])
arcid={**{n:0 for n in range(21,28)},**{n:1 for n in range(29,36)},**{n:2 for n in range(37,43)},**{n:3 for n in range(44,49)}}
t_obs=np.array([cap(n) for n in use])/25.
u_obs=np.array([tr[src][n]['cx'] for n in use]); v_obs=np.array([tr[src][n]['cy'] for n in use])
a_obs=np.array([arcid[n] for n in use])
PRIOR=np.zeros(2); PSIG=np.radians(6)
for a in sys.argv:
    if a.startswith('fix='):
        pp,rr=a[4:].split(','); PRIOR=np.radians([float(pp),float(rr)]); PSIG=np.radians(0.05)
TOF=('tof' in sys.argv); CARD=('card' in sys.argv)
if 'wc' in sys.argv:
    u_obs=np.array([wd[src][str(n)]['cx'] for n in use]); v_obs=np.array([wd[src][str(n)]['cy'] for n in use])
def basis(pitch,roll):
    # gravity 'down' unit vector in camera coords (x right, y down, z fwd)
    d=np.array([0,1,0.])
    cp,sp=np.cos(pitch),np.sin(pitch); cr,sr=np.cos(roll),np.sin(roll)
    Rx=np.array([[1,0,0],[0,cp,-sp],[0,sp,cp]]); Rz=np.array([[cr,-sr,0],[sr,cr,0],[0,0,1]])
    down=Rz@Rx@d
    e1=np.cross(down,[0,0,1.]); e1/=np.linalg.norm(e1)   # horizontal, roughly camera x
    e2=np.cross(e1,down); e2/=np.linalg.norm(e2)          # horizontal, roughly forward
    return down,e1,e2
NA=4
def unpack(p):
    pitch,roll,Hc=p[0],p[1],p[2]
    T=p[3:3+NA+1]           # bounce times (s): T0..T4
    h0=p[8:10]              # horizontal coords at T0 (along e1,e2)
    if shared:
        vel=np.tile(p[10:12],(NA,1)); 
    else:
        vel=p[10:10+2*NA].reshape(NA,2)
    return pitch,roll,Hc,T,h0,vel
def positions(p,t,a):
    pitch,roll,Hc,T,h0,vel=unpack(p)
    down,e1,e2=basis(pitch,roll)
    # horizontal position at each bounce
    hb=[np.array(h0)]
    for i in range(NA): hb.append(hb[-1]+vel[i]*(T[i+1]-T[i]))
    P=[]
    for ti,ai in zip(t,a):
        dt=ti-T[ai]; Ta=T[ai+1]-T[ai]
        h=hb[ai]+vel[ai]*dt
        # height above bounce plane: g*dt*(Ta-dt)/2 (upwards = -down)
        z=0.5*g*dt*(Ta-dt)
        P.append(h[0]*e1+h[1]*e2+(Hc-z)*down)
    return np.array(P)
def resid(p):
    P=positions(p,t_obs,a_obs)
    u=CX+f*P[:,0]/P[:,2]; v=CY+f*P[:,1]/P[:,2]
    r=[u-u_obs,v-v_obs]
    # weak priors: pitch, roll ~ N(0, 3deg)
    r.append((np.array([p[0],p[1]])-PRIOR)/PSIG)
    if CARD:
        down,_,_=basis(p[0],p[1])
        uc=np.array([(561-CX)/f,(540-CY)/f,1.]); uc/=np.linalg.norm(uc)
        r.append(np.array([(p[2]+0.02-down@(0.679*uc))/0.006]))
    if TOF: 
        Pa=positions(p,np.array([25/25.]),np.array([0]))[0]
        r.append(np.array([(np.linalg.norm(Pa)-0.02-1.055)/0.01]))
    return np.concatenate(r)
# init
p0=[0.0,0.0,0.14, 20.5/25,29.2/25,37.75/25,45.5/25,53/25, -0.0,1.15]
p0+= [-0.47,-0.3] if shared else [-0.47,-0.3]*NA
best=None
for Hc0 in [0.10,0.14,0.18]:
    q=np.array(p0,float); q[2]=Hc0
    r=least_squares(resid,q,iters=500)
    c=r.fun@r.fun
    if best is None or c<best[0]: best=(c,r)
r=best[1]; p=r.x
pitch,roll,Hc,T,h0,vel=unpack(p)
P=positions(p,t_obs,a_obs)
nres=len(t_obs)*2
print('src',src,'shared' if shared else 'perarc','rms px %.2f'%np.sqrt(np.mean(r.fun[:nres]**2)))
print('pitch %.2f deg roll %.2f deg Hc %.4f m (table dist %.4f)'%(np.degrees(pitch),np.degrees(roll),Hc,Hc+0.02))
print('bounce caps',np.round(T*25,2))
print('h0',np.round(h0,3),'vel per arc',np.round(vel,3))
# covariance
J=r.J[:nres]; s2=np.mean(r.fun[:nres]**2)
try:
    cov=np.linalg.inv(r.J.T@r.J)*s2
except Exception: cov=None
# Evaluate at caps of interest
tq=np.arange(22,51)/25.
aq=np.array([0 if c<T[1]*25 else 1 if c<T[2]*25 else 2 if c<T[3]*25 else 3 for c in tq*25])
Pq=positions(p,tq,aq)
for c,PP in zip(range(22,51),Pq):
    if c in (24,25,26,27,33,34,35,36,37,41,49):
        print('cap',c,'C=',np.round(PP,4),'range %.4f'%np.linalg.norm(PP), 'u,v=%.1f,%.1f'%(CX+f*PP[0]/PP[2],CY+f*PP[1]/PP[2]))
def vel_label(c):
    i=c-22
    A=Pq[i]; B=Pq[i+1]
    phys=np.linalg.norm(B-A)*25
    # label style: surface point along the ray of the centre at range |C|-R
    R=0.02
    As=A*(np.linalg.norm(A)-R)/np.linalg.norm(A); Bs=B*(np.linalg.norm(B)-R)/np.linalg.norm(B)
    lab=np.linalg.norm(Bs-As)*25
    return phys,lab
for c in (25,35):
    ph,lb=vel_label(c)
    print('v fwd cap %d->%d: physical-centre %.1f cm/s, label-style(surface) %.1f cm/s'%(c,c+1,ph*100,lb*100))
np.save('gfit_%s_%s.npy'%(src,'shared' if shared else 'perarc'),p)
if cov is not None:
    # MC propagate
    rng=np.random.default_rng(0); vals=[]
    for k in range(300):
        pp=rng.multivariate_normal(p,cov)
        Pm=positions(pp,tq,aq)
        vals.append([np.linalg.norm(Pm[c-22+1]-Pm[c-22])*25 for c in (25,35)])
    vals=np.array(vals)*100
    print('MC sd of physical v: cap25 %.1f, cap35 %.1f'%tuple(vals.std(0)))
