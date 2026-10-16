import numpy as np, json
rows=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0010/track_s.json'))
f=711.0; cx0=640.0; cy0=360.0; D=0.07
t=np.array([r['f'] for r in rows])/24.0
u=np.array([r['u'] for r in rows]); v=np.array([r['v'] for r in rows])
Dx=np.array([r['Dx'] for r in rows]); Dy=np.array([r['Dy'] for r in rows])
# use Dx (perp to the mostly-vertical image motion)
Z=f*D/Dx
X=(u-cx0)*Z/f; Y=(v-cy0)*Z/f
P=np.stack([X,Y,Z],1)
# given depth check
gd={0.3:1.7060,0.6:1.3440,0.9:1.4605,1.2:1.7840,1.5:1.7170,1.8:1.3500}
for tt,dd in gd.items():
    i=tt*24; Zi=np.interp(i,np.arange(49),Z); ui=np.interp(i,np.arange(49),u); vi=np.interp(i,np.arange(49),v)
    rng=Zi*np.sqrt(1+((ui-cx0)**2+(vi-cy0)**2)/f**2)
    Dxi=np.interp(i,np.arange(49),Dx)
    print(f"t={tt} given={dd} size-range={rng:.3f} ratio={dd/rng:.3f}  D_from_given={Dxi*dd/np.sqrt(1+((ui-cx0)**2+(vi-cy0)**2)/f**2)/f*100:.2f}cm")
def basis(t,w):
    return np.stack([np.ones_like(t),t,np.cos(w*t),np.sin(w*t),np.cos(2*w*t),np.sin(2*w*t)],1)
def fitw(w):
    B=basis(t,w); C,*_=np.linalg.lstsq(B,P,rcond=None); return C, np.sum((B@C-P)**2)
ws=np.linspace(3.5,6.5,3001); costs=[fitw(w)[1] for w in ws]
wb=ws[int(np.argmin(costs))]; C,_=fitw(wb)
p=(wb,C)
def model(p,t,k):
    w,C=p; return basis(np.atleast_1d(t),w)@C
class R: pass
best=R(); best.fun=(model(p,t,0)-P).ravel()
w=p[0]; T=2*np.pi/w
print('omega',w,'T',T,'rms resid (cm)',np.sqrt(np.mean(best.fun**2))*100)
Pm=model(p,t,0)
for j,nm in enumerate('XYZ'): print(nm,'rms',np.sqrt(np.mean((Pm[:,j]-P[:,j])**2))*100,'cm')
def vel(tq,h=1e-4): return (model(p,np.array([tq+h]),0)-model(p,np.array([tq-h]),0))[0]/(2*h)
def acc(tq,h=1e-3): return (model(p,np.array([tq+h]),0)-2*model(p,np.array([tq]),0)+model(p,np.array([tq-h]),0))[0]/h**2
for tq in [0.3,0.6,0.9,1.2,1.5]:
    vv=vel(tq); aa=acc(tq)
    print(f"t={tq}: |v|={np.linalg.norm(vv):.3f} m/s v={np.round(vv,3)} |a|={np.linalg.norm(aa):.3f} m/s2")
# chord velocities between labelled times using model positions
for a,b in [(0.3,0.6),(0.6,0.9)]:
    pa=model(p,np.array([a]),0)[0]; pb=model(p,np.array([b]),0)[0]
    print(f"chord {a}->{b}: {np.linalg.norm(pb-pa)/(b-a):.3f} m/s")
# forward differences 1 frame on model
for tq in [0.3,0.6]:
    for dt in [1/24,1/25,2/24]:
        pa=model(p,np.array([tq]),0)[0]; pb=model(p,np.array([tq+dt]),0)[0]
        print(f"fwd t={tq} dt={dt:.4f}: {np.linalg.norm(pb-pa)/dt:.3f}")
# pendulum geometry: fit pivot as point equidistant from all model positions
tt=np.linspace(0,2,200); Q=model(p,tt,0)
A=np.c_[2*Q,np.ones(len(Q))]; bb=(Q**2).sum(1)
sol,*_=np.linalg.lstsq(A,bb,rcond=None); q=sol[:3]; L=np.sqrt(sol[3]+q@q)
print('pivot',q,'L',L,'resid rms cm',np.std(np.linalg.norm(Q-q,axis=1))*100)

print('--- planar circle fit ---')
Qc=Q-Q.mean(0); U,S,Vt=np.linalg.svd(Qc,full_matrices=False)
print('singular values',S, 'plane normal',Vt[2])
e1,e2=Vt[0],Vt[1]
q2=np.c_[Qc@e1,Qc@e2]
A=np.c_[2*q2,np.ones(len(q2))]; bb=(q2**2).sum(1)
sol,*_=np.linalg.lstsq(A,bb,rcond=None); c2=sol[:2]; Lc=np.sqrt(sol[2]+c2@c2)
piv=Q.mean(0)+c2[0]*e1+c2[1]*e2
print('circle pivot 3D',piv,'pix',640+711*piv[0]/piv[2],360+711*piv[1]/piv[2],'L',Lc,'rms',np.std(np.linalg.norm(q2-c2,axis=1))*100,'cm')
print('--- pivot constrained to observed string-top ray ---')
for (pu,pv) in [(639,226),(637,220),(640,232),(632,212)]:
    ray=np.array([(pu-640)/711,(pv-360)/711,1.0])
    best=None
    for dz in np.linspace(1.2,1.9,1401):
        q=ray*dz; dist=np.linalg.norm(Q-q,axis=1)
        c=np.std(dist)
        if best is None or c<best[0]: best=(c,dz,dist.mean())
    print(f'pivot pix ({pu},{pv}) Z={best[1]:.3f} L={best[2]:.3f} spread={best[0]*100:.2f}cm')
# amplitude
print('Z range of model',Q[:,2].min(),Q[:,2].max())
