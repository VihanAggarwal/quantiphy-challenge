import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0035/scripts')
from recon import *
tr=load('ax'); bb=tr['bb']; sb=tr['sb']
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)
T={k:orig(k)/25.0 for k in range(49)}
Ds=0.181
for key,D,rng in [('sb',Ds,range(30,48)),('bb',0.232,range(24,49)),('sb',Ds,range(32,42)),('bb',0.232,range(32,42))]:
    t=np.array([T[k] for k in rng]); d=np.array([tr[key][k]['minor'] for k in rng]); dq=np.array([np.sqrt(4*tr[key][k]['A']/np.pi) for k in rng])
    for nm,sz in [('minor',d),('deq',dq)]:
        R=F*D/sz
        pr=np.polyfit(t,R,1)
        u=np.array([tr[key][k]['cx'] for k in rng]); w=np.array([tr[key][k]['cy'] for k in rng])
        # lateral: angular rate * range
        ang=np.array([ray(a,b) for a,b in zip(u,w)])
        P=R[:,None]*ang
        # fit P linear with smoothed R
        Rs=np.polyval(pr,t); Psm=Rs[:,None]*ang
        cf=np.polyfit(t,Psm,1)[0]
        print(key,nm,'frames',rng[0],rng[-1],'dR/dt cm/s %.1f'%(pr[0]*100),'speed(smoothed R) %.1f'%(np.linalg.norm(cf)*100))
