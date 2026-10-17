# Person ground speed in 0027 for a range of camera pitch values (f=3404 from 0028 same camera; roll 0)
import numpy as np, pandas as pd
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1/'
p=pd.read_csv(W+'p27b.csv'); f=3403.7; c=480.0
t=p.frame.values/24.0
# linear fits of image tracks (whole clip, ~4.2 steps) and over t in [1,2]
def slope(x,tt): A=np.c_[np.ones_like(tt),tt]; return np.linalg.lstsq(A,x,rcond=None)[0]
for nm,(xs,ys) in {'shirt':(p.shirt_x.values,p.shirt_y.values),'tip':(p.tip_x.values,p.tip_y.values)}.items():
    print(nm,'full slope px/s',slope(xs,t)[1].round(2),slope(ys,t)[1].round(2),
          ' t1-2 chord',(xs[48]-xs[24]).round(2),(ys[48]-ys[24]).round(2))
hpx=(p.foot-(p.shirt_top-10)).values
print('pixel height (foot - (shirt_top-10)): mean %.1f med %.1f'%(hpx.mean(),np.median(hpx)))
def ground_pts(u,v,th,Hc,hgt):
    th=np.radians(th); n=np.array([0,-np.cos(th),-np.sin(th)])
    R=np.c_[(u-c)/f,(v-c)/f,np.ones_like(u)]
    lam=-(Hc-hgt)/(R@n)      # plane X.n = -(Hc-hgt)
    return R*lam[:,None]
for th in [16,17,18,19,20,21,22,24,26]:
    thr=np.radians(th); n=np.array([0,-np.cos(thr),-np.sin(thr)])
    # anchor A: pelvis range = 100.58 (depth label mean); find Hc s.t. pelvis (foot ray ground pt + 0.95 n) has range 100.58 at t=1.5
    i=36
    u_f,v_f=p.foot_x.values[i],p.foot.values[i]+0.5
    Rf=np.array([(u_f-c)/f,(v_f-c)/f,1.0])
    def pelvis_range(Hc):
        F=Rf*(-Hc/(Rf@n)); return np.linalg.norm(F+0.95*n)
    lo,hi=1,90
    for _ in range(60):
        m=0.5*(lo+hi)
        if pelvis_range(m)>100.58: hi=m
        else: lo=m
    HcA=0.5*(lo+hi)
    # anchor B: height prior: head (1.75) above foot projects to measured pixel height (median)
    def pix_h(Hc):
        F=Rf*(-Hc/(Rf@n)); Hd=F+1.75*n
        return (c+f*F[1]/F[2])-(c+f*Hd[1]/Hd[2])
    lo,hi=1,90
    for _ in range(60):
        m=0.5*(lo+hi)
        if pix_h(m)>np.median(hpx): lo=m
        else: hi=m
    HcB=0.5*(lo+hi)
    out=[]
    for Hc in (HcA,HcB):
        G=ground_pts(p.shirt_x.values,p.shirt_y.values,th,Hc,1.15)   # shirt centroid ~1.15 m above ground
        # horizontal displacement: remove n component
        Gh=G-np.outer(G@n,n)
        vfit=np.array([slope(Gh[:,k],t)[1] for k in range(3)])
        chord=np.linalg.norm(Gh[48]-Gh[24])
        F=Rf*(-Hc/(Rf@n))
        out.append((Hc,np.linalg.norm(F),np.linalg.norm(vfit),chord))
    print(f'theta {th:4.1f}: depth-anchored Hc {out[0][0]:.1f} footR {out[0][1]:.1f} speed fit {out[0][2]:.3f} chord {out[0][3]:.3f} | height-anchored Hc {out[1][0]:.1f} footR {out[1][1]:.1f} speed fit {out[1][2]:.3f} chord {out[1][3]:.3f}')
