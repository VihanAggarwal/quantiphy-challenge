# Sensitivity sweep: plane route (floor fit from ToF + size trajectories) -> soccer ball velocity at capture 40->41.
import json, numpy as np
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0035/rm2/track_ax.json'))
def cap(i): return int(np.floor(i*25/24+0.5))
def series(key,i0,i1):
    return np.array([(cap(i),T[str(i)][key]['cxw'],T[str(i)][key]['cyw'],T[str(i)][key]['dsoft']) for i in range(i0,i1+1) if key in T[str(i)]])
sb=series('sb',21,47); bb=series('bb',21,48)
def nvec(th,ph): return np.array([np.sin(th)*np.cos(ph),-np.cos(th),np.sin(th)*np.sin(ph)])
def run(f=711.,cx=640.,cy=360.,Rs=0.095,Rb=0.116,mode='traj+tof',vel_win=(31,49)):
    def ray(u,v):
        d=np.array([(u-cx)/f,(v-cy)/f,1.]);return d/np.linalg.norm(d)
    def anchorK(S,j,rs,R):
        m=abs(S[:,0]-j)<=8; p=np.polyfit(S[m,0],S[m,3],1); return (rs+R)*np.polyval(p,j)
    Ks=anchorK(sb,40,3.052,Rs); Kb=anchorK(bb,40,2.412,Rb)
    pts=[]
    if 'traj' in mode:
        pts+=[(ray(u,v)*(Ks/d),Rs) for _,u,v,d in sb]+[(ray(u,v)*(Kb/d),Rb) for _,u,v,d in bb]
    s14=T['14']['sb']; b14=T['14']['bb']; s38=T['38']['sb']; b38=T['38']['bb']
    tof=[(ray(s14['cxw'],s14['cyw'])*(2.758+Rs),Rs),(ray(b14['cxw'],b14['cyw'])*(2.270+Rb),Rb),
         (ray(s38['cxw'],s38['cyw'])*(3.052+Rs),Rs),(ray(b38['cxw'],b38['cyw'])*(2.412+Rb),Rb)]
    if 'tof' in mode: pts+=tof*(5 if 'traj' in mode else 1)
    P=np.array([p for p,_ in pts]); R=np.array([r for _,r in pts])
    best=None
    for th in np.radians(np.arange(10,70,0.25)):
        for ph in np.radians(np.arange(0,360,1.0)):
            n=nvec(th,ph); r=P@n-R; c=-r.mean(); e=np.mean((r+c)**2)
            if best is None or e<best[0]: best=(e,th,ph,c)
    _,th,ph,c=best; n=nvec(th,ph)
    J=sb[:,0]
    C=np.array([ray(u,v)*((Rs-c)/(n@ray(u,v))) for _,u,v,_ in sb])     # centres on plane
    S=np.array([p-Rs*p/np.linalg.norm(p) for p in C])                     # visible surface point along same ray
    m=(J>=vel_win[0])&(J<=vel_win[1]); tt=J[m]/25.
    vc=np.array([np.polyfit(tt,C[m,k],1)[0] for k in range(3)])
    vs=np.array([np.polyfit(tt,S[m,k],1)[0] for k in range(3)])
    r40=ray(T['38']['sb']['cxw'],T['38']['sb']['cyw'])
    k40=np.where(J==40)[0][0]
    return dict(pitch=np.degrees(th),cam_h=c,rng40=np.linalg.norm(C[k40]),v_centre=np.linalg.norm(vc)*100,v_surface=np.linalg.norm(vs)*100,
                range_rate=(vc@r40)*100,lateral=np.linalg.norm(vc-(vc@r40)*r40)*100,raw_fd=np.linalg.norm(S[k40+1]-S[k40])*2500)
base=run()
print('BASE',{k:round(v,3) for k,v in base.items()})
for kw in [dict(mode='tof'),dict(mode='traj'),dict(f=680.),dict(f=750.),dict(f=800.),dict(Rs=0.085),dict(Rs=0.105),
           dict(cx=620.),dict(cx=660.),dict(cy=340.),dict(cy=380.),dict(vel_win=(35,46)),dict(vel_win=(33,49))]:
    r=run(**kw); print(kw,{k:round(v,2) for k,v in r.items()})
