# distance travelled until the hit (n31 = video 30): interpretation I (from t=1.0 = video 24) and II (from the
# start of the motion: ball held in the hand at the front-right corner, video 0-17)
import numpy as np, json, cv2
from frames import frames
from geom import ray, pose, on_plane
f=711.
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/track.json'))
o=T['o']; x=T['x']
uv={k:np.array([(o[k]['cx']+x[k]['cx'])/2,(o[k]['cy']+x[k]['cy'])/2]) for k in range(49)}
def unit(p): d=ray(*p,f); return d/np.linalg.norm(d)
P24=0.901*unit(uv[24]); P30=1.144*unit(uv[30])
print('I  chord (stated depths, clicked centres) = %.1f cm'%(100*np.linalg.norm(P30-P24)))
# MC with 2 px click jitter
rng=np.random.default_rng(0); L=[]
for i in range(20000):
    a=0.901*unit(uv[24]+rng.normal(0,2,2)); b=1.144*unit(uv[30]+rng.normal(0,2,2)); L.append(100*np.linalg.norm(b-a))
print('   MC click jitter: q5/50/95 = %.1f/%.1f/%.1f'%tuple(np.percentile(L,[5,50,95])))
# path version: sum of forward differences n25..n31 with intermediate ToF = route range + noise
RT=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/routes3d.json'))
for nm in ['A_pnp','B_anchorplane']:
    P={int(k):np.array(v) for k,v in RT[nm].items()}
    print('   %s physical path video24->30 %.1f, chord %.1f'%(nm,100*sum(np.linalg.norm(P[k+1]-P[k]) for k in range(24,30)),100*np.linalg.norm(P[30]-P[24])))
    for sz in [0.01,0.02]:
        Ls=[]
        rs={k:np.linalg.norm(P[k])-0.0335 for k in range(24,31)}
        rs[24]=0.901; rs[30]=1.144
        for i in range(5000):
            Q=[ (rs[k]+(rng.normal(0,sz) if k not in (24,30) else 0))*unit(uv[k]+rng.normal(0,2,2)) for k in range(24,31)]
            Ls.append(100*sum(np.linalg.norm(Q[j+1]-Q[j]) for j in range(6)))
        print('   path label (sum of 6 clicked steps, sigma_z %.0f cm): q5/50/95 = %.1f/%.1f/%.1f'%(100*sz,*np.percentile(Ls,[5,50,95])))
# II: start position. Sphere image model: semi-minor axis b for a sphere of radius r at centre range R, off-axis.
def sphere_ellipse(Pc,r=0.0335):
    R=np.linalg.norm(Pc); u=Pc/R; a=np.arcsin(r/R)
    e1=np.cross(u,[0,1,0]); e1/=np.linalg.norm(e1); e2=np.cross(u,e1)
    th=np.linspace(0,2*np.pi,360,endpoint=False)
    rays=np.cos(a)*u[None]+np.sin(a)*(np.cos(th)[:,None]*e1+np.sin(th)[:,None]*e2)
    pts=(rays[:,:2]/rays[:,2:]*f+[640,360]).astype(np.float32)
    (cx,cy),(w,h),ang=cv2.fitEllipse(pts); return min(w,h),max(w,h)
S=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/sizefit.json'))
for k in [0,4,8,12,16,17]:
    t=x[k]; mn,mj=t['ell'][2],t['ell'][3]
    # solve range so that the model minor axis equals the measured one
    u=unit(uv[k]); Rs=np.linspace(0.4,0.9,501); m=np.array([sphere_ellipse(R_*u)[0] for R_ in Rs])
    R_=Rs[np.argmin(np.abs(m-mn))]
    Pst=(R_-0.0335)*u   # surface-range point along the clicked ray (as the labeller back-projects)
    print('II start video %2d: centre (%.0f,%.0f) minor %.1f major %.1f -> centre range %.3f; chord to hit (stated 1.144) = %.1f cm'%(k,*uv[k],mn,mj,R_,100*np.linalg.norm(P30-Pst)))
R,t,n,d0,err=pose()
for k in [17,18,19,20]:
    Pp=on_plane(*uv[k],R,t,n,d0,0.0335); print('   plane-route centre range video %d: %.3f; chord(surface) to hit %.1f'%(k,np.linalg.norm(Pp),100*np.linalg.norm(P30-(np.linalg.norm(Pp)-0.0335)*unit(uv[k]))))
