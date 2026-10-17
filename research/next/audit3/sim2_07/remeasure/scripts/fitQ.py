import json, numpy as np, sys
rows=json.load(open('diam2_simulation_0254.json'))
R={int(r[0]):r for r in rows}
lo,hi=int(sys.argv[1]),int(sys.argv[2])
fr=np.array(sorted(i for i in R if lo<=i<=hi))
cx=np.array([R[i][5] for i in fr]); cy=np.array([R[i][6] for i in fr])
d=np.array([np.cos(np.radians(44.224)),np.sin(np.radians(44.224))])
s=cx*d[0]+cy*d[1]; t=fr/24.0
def xQ(a0,V,tau):
    tau=np.maximum(tau,0); z=a0*tau/V
    return (V**2/a0)*(z+np.log1p(np.exp(-2*z))-np.log(2))
def vQ(a0,V,tau):
    tau=np.maximum(tau,0); return V*np.tanh(a0*tau/V)
Vg=np.linspace(800,12000,561)[:,None,None]; Ag=np.linspace(700,1700,251)[None,:,None]
def search(t0s):
    best=None
    for t0 in t0s:
        X=xQ(Ag,Vg,(t-t0)[None,None,:])
        r=s[None,None,:]-X; r=r-r.mean(2,keepdims=True); E=(r**2).sum(2)
        i=np.unravel_index(np.argmin(E),E.shape)
        if best is None or E[i]<best[0]: best=(E[i],Ag[0,i[1],0],Vg[i[0],0,0],t0)
    return best
for t0s,lab in ((np.linspace(-0.3,0.3,121),'free'),([0.0],'t0=0'),([-1/24],'t0=-1f'),([1/24],'t0=+1f')):
    e,a0,V,t0=search(t0s)
    c=a0/V**2
    out=f'Q {lab}: a0={a0:.1f} V={V:.0f} c={c:.3e} t0={t0:.3f} rms={np.sqrt(e/len(t)):.3f}px |'
    for tq in (0.5,1.0,1.5,1.75):
        xs=xQ(a0,V,np.array([tq-2/24,tq-1/24,tq])-t0)
        vb=(xs[2]-xs[1])*24; vb1=(xs[1]-xs[0])*24
        vi=vQ(a0,V,tq-t0); ai=a0-c*vi**2
        out+=f' t={tq}: vb={vb:.1f} ab={(vb-vb1)*24:.1f} ai={ai:.1f};'
    print(out)
