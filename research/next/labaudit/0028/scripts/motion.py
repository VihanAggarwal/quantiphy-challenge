import numpy as np
F=711;CX=640;CY=360
trk={20:(722.2,289.8),21:(724.3,290.8),22:(726.8,297.7),23:(729.5,312.8),24:(731.5,335.7),25:(733.9,369.0),26:(736.8,406.0),27:(738.9,388.9),28:(741.5,356.1),29:(743.8,330.2),30:(745.7,313.7),31:(747.8,303.2),32:(749.7,300.0),33:(751.6,303.9),34:(753.4,315.5),35:(755.2,338.4)}
ts=np.array(sorted(trk)); U=np.array([trk[t] for t in ts])
def uv(n): return np.array([np.interp(n,ts,U[:,0]),np.interp(n,ts,U[:,1])])
def P(n,r):
    u,v=uv(n); d=np.array([(u-CX)/F,(v-CY)/F,1.0]); return r*d/np.linalg.norm(d)
for fps in (24,25):
    an=[(1.0*fps,1.805),(1.1*fps,1.557),(1.3*fps,1.4115)]
    def R(n): return np.interp(n,[a for a,_ in an],[b for _,b in an])
    def Pt(t): n=t*fps; return P(n,R(n))
    dt=1/fps
    v10=np.linalg.norm(Pt(1.0+dt)-Pt(1.0))/dt*100
    v13=np.linalg.norm(Pt(1.3+dt)-Pt(1.3))/dt*100   # beyond 1.3 range is held constant
    v13b=np.linalg.norm(Pt(1.3)-Pt(1.3-dt))/dt*100
    st=np.linalg.norm(Pt(1.3)-Pt(1.1))*100
    tt=np.arange(1.1,1.3+1e-9,dt); path=sum(np.linalg.norm(Pt(b)-Pt(a)) for a,b in zip(tt[:-1],tt[1:]))*100
    # constant-range variants for v(1.0)
    v10c=np.linalg.norm(P(fps*1.0+1,1.805)-P(fps*1.0,1.805))*fps*100
    print(f'fps {fps}: v(1.0) interp-depth {v10:.0f}, const-depth {v10c:.0f}; v(1.3) fwd {v13:.0f} (depth flat after) back {v13b:.0f}; dist 1.1-1.3 straight {st:.1f} path {path:.1f}')
