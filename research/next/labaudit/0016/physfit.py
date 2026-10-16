import numpy as np
import sys; sys.path.insert(0,"."); from lm import least_squares
f=711.;cx,cy=640,360;g0=9.8
obs={32:(586.8,256.2),33:(640.8,198.8),34:(688.7,156.0),35:(735.2,121.1),36:(812.2,77.2),37:(844.7,70.3),38:(872.3,70.5),39:(894.5,77.3),40:(913.1,90.6)}
size={32:97.2,33:94.6,34:94.7,35:97.9,36:89.1,37:90.8,38:91.2,39:88.8,40:84.6}
def run(tmap,anchor_range=1.402,use_size=False,label=''):
    fr=sorted(obs); t=np.array([tmap[k] for k in fr]); uv=np.array([obs[k] for k in fr])
    def pos(p,tt):
        P0=p[0:3];V=p[3:6];th,ph=p[6],p[7]
        gd=np.array([np.sin(ph)*np.cos(th),np.cos(ph)*np.cos(th),np.sin(th)])
        return P0[None]+V[None]*tt[:,None]+0.5*g0*gd[None]*tt[:,None]**2
    def res(p):
        P=pos(p,t-tmap[36])
        u=cx+f*P[:,0]/P[:,2];v=cy+f*P[:,1]/P[:,2]
        r=list(u-uv[:,0])+list(v-uv[:,1])
        P36=pos(p,np.array([0.]))[0]
        r.append((np.linalg.norm(P36)-anchor_range)*500)  # 2mm ~ 1px
        if use_size:
            s=p[8]; pred=f*s/P[:,2]; r+=list((pred-np.array([size[k] for k in fr]))*0.5)
        return np.array(r)
    best=None
    for th0 in np.linspace(0.2,1.2,6):
        for vz in [-2,0,2,4]:
            p0=[0.3,-0.5,1.27,2,-1,vz,th0,0.0]+([0.17] if use_size else [])
            r=least_squares(res,p0)
            if best is None or r.cost<best.cost: best=r
    p=best.x; rr=res(p)
    V36=p[3:6]
    gd=np.array([np.sin(p[7])*np.cos(p[6]),np.cos(p[7])*np.cos(p[6]),np.sin(p[6])])
    dt=1/24
    P=pos(p,np.array([0,dt]));fwd=np.linalg.norm(P[1]-P[0])/dt
    print(label,'rms px',round(np.sqrt(np.mean(rr[:2*len(fr)]**2)),2),'pitch deg',round(np.degrees(p[6]),1),'roll',round(np.degrees(p[7]),1),'V36',V36.round(2),'|V|',round(np.linalg.norm(V36),2),'fwd36->37',round(fwd,2), ('D=%.3f'%p[8] if use_size else ''))
    return best
uni={k:k/24 for k in obs}
run(uni,label='uniform')
run(uni,use_size=True,label='uniform+size')
drop={k:(k/24 if k<=35 else (k+1)/24) for k in obs}
run(drop,label='drop35/36')
run(drop,use_size=True,label='drop+size')
# drop at 30fps capture timing
for name,tm in [('30fps-uniform',{k:k/30 for k in obs})]:
    run(tm,label=name)
