# Joint camera-pitch / sun / ground fit for the 0027/0028 camera (identical backgrounds).
# Data: 0028 eagle 3D (f from stated eagle speed, ranges) + eagle-shadow pixels; 0027 person foot, head-shadow tip.
import numpy as np, pandas as pd, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1')
from geom import P3
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1/'
f=3403.7; c=480.0; H=1.75
# --- 0028 eagle and shadow per frame
d=pd.read_csv(W+'e28.csv')
eg=d[(d.cy<300)&(d.area>100)].sort_values(['frame','area'],ascending=[True,False]).groupby('frame').first()
sh=d[(d.cy>340)&(d.cy<400)&(d.area>150)&(d.cx<830)].sort_values(['frame','area'],ascending=[True,False]).groupby('frame').first()
fr=sorted(set(eg.index)&set(sh.index)); fr=[k for k in fr if k<=28]
E1=P3(456.87,243.87,100.1405,f); E2=P3(864.77,254.61,99.5206,f)
def Eline(t): return E1+(t-1)*(E2-E1)
E=np.array([np.linalg.norm(Eline(k/24))*np.array([(eg.loc[k,'cx']-c)/f,(eg.loc[k,'cy']-c)/f,1])/np.linalg.norm([(eg.loc[k,'cx']-c)/f,(eg.loc[k,'cy']-c)/f,1]) for k in fr])
Sobs=np.array([[sh.loc[k,'cx'],sh.loc[k,'cy']] for k in fr])
# --- 0027 person
p=pd.read_csv(W+'p27b.csv')
p=p[p.frame%3==0]
Fobs=p[['foot_x','foot']].values.astype(float)+np.array([0,0.5])
Tobs=p[['tip_x','tip_y']].values.astype(float)
Hobs=np.c_[p.shirt_x.values,p.shirt_top.values-10.0]
def proj(X): return np.c_[c+f*X[:,0]/X[:,2], c+f*X[:,1]/X[:,2]]
def model(par):
    th,az,el,Hc=par
    th=np.radians(th); az=np.radians(az); el=np.radians(el)
    n=np.array([0,-np.cos(th),-np.sin(th)])          # world up in camera coords
    fwd=np.array([0,-np.sin(th),np.cos(th)])          # world horizontal forward
    rgt=np.array([1.0,0,0])
    s=np.cos(el)*(np.sin(az)*rgt+np.cos(az)*fwd)+np.sin(el)*n   # unit vector toward sun
    # eagle shadows
    a=E@n+Hc
    S=E-(a/(s@n))[:,None]*s[None,:]
    # person: foot on ground
    rays=np.c_[(Fobs[:,0]-c)/f,(Fobs[:,1]-c)/f,np.ones(len(Fobs))]
    lam=-Hc/(rays@n); F=rays*lam[:,None]
    Hd=F+H*n
    T=Hd-(H/(s@n))*s
    return proj(S),proj(T),proj(Hd),F
def resid(par,wh=0.3):
    S,T,Hd,F=model(par)
    return np.r_[(S-Sobs).ravel(),(T-Tobs).ravel(),wh*(Hd-Hobs).ravel()]
def gn(par,wh=0.3,it=60):
    par=np.array(par,float)
    for _ in range(it):
        r=resid(par,wh); J=np.zeros((len(r),4))
        for j in range(4):
            dp=np.zeros(4); dp[j]=1e-4*max(1,abs(par[j]))
            J[:,j]=(resid(par+dp,wh)-r)/dp[j]
        step=np.linalg.lstsq(J,-r,rcond=None)[0]
        par=par+0.7*step
    return par,resid(par,wh)
best=None
for th0 in [10,18,26,34]:
  for az0 in [-120,-90,-60,60,90,120,180,0]:
    for el0 in [20,35]:
        try:
            par,r=gn([th0,az0,el0,30],it=40)
        except Exception: continue
        sse=(r**2).sum()
        if np.isfinite(sse) and (best is None or sse<best[0]): best=(sse,par)
sse,par=best
print('best params th,az,el,Hc:',par.round(3),'rms',np.sqrt(sse/len(resid(par))))
S,T,Hd,F=model(par)
print('person foot ranges (first,last):',np.linalg.norm(F,axis=1)[[0,-1]].round(2),' pelvis range at t~1:',np.linalg.norm(F[8]+0.95*np.array([0,-np.cos(np.radians(par[0])),-np.sin(np.radians(par[0]))])).round(2))
print('shadow resid rms',np.sqrt(((S-Sobs)**2).mean()).round(2),' tip resid rms',np.sqrt(((T-Tobs)**2).mean()).round(2),' head resid rms',np.sqrt(((Hd-Hobs)**2).mean()).round(2))
# profile over theta
for th in np.arange(12,32,2.0):
    def r2(q): return resid(np.r_[th,q])
    q=np.array(par[1:],float)
    for _ in range(40):
        r=r2(q); J=np.zeros((len(r),3))
        for j in range(3):
            dq=np.zeros(3); dq[j]=1e-4*max(1,abs(q[j])); J[:,j]=(r2(q+dq)-r)/dq[j]
        q=q+0.7*np.linalg.lstsq(J,-r,rcond=None)[0]
    r=r2(q); S,T,Hd,F=model(np.r_[th,q])
    print(f'theta {th:5.1f} az {q[0]:7.2f} el {q[1]:6.2f} Hc {q[2]:6.2f} rms {np.sqrt((r**2).mean()):.2f}  S {np.sqrt(((S-Sobs)**2).mean()):.2f} T {np.sqrt(((T-Tobs)**2).mean()):.2f} Hd {np.sqrt(((Hd-Hobs)**2).mean()):.2f} footR {np.linalg.norm(F[8]):.1f}')
