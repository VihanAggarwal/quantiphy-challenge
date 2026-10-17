from common import *
from tracks import *
from fit_a import fit, model, gd, proj
db=np.load(OUT+'/b_down.npy')
def gr(p,r):
    p=np.radians(p); r=np.radians(r); return np.array([np.sin(r)*np.cos(p),np.cos(r)*np.cos(p),np.sin(p)])
R=0.0335
cases=[('a','W',A_W,list(range(24,38)),3.0735,[gd(0),gd(1),gd(2)]),('a','G',A_G_raw,list(range(24,37)),3.039,[gd(0),gd(1),gd(2)]),
       ('b','W',B_W,list(range(24,39)),1.235,[db,gr(29.9,-6.5)]),('b','G',B_G,list(range(24,37)),1.331,[db,gr(29.9,-6.5)])]
for cam,ball,tr,ks,rs,gs in cases:
    for g in gs:
        p,rms=fit(tr,ks,g)
        C=lambda t: model(p,np.array([t]),1.0,g)[0]
        s=rs/(np.linalg.norm(C(1.0))-R)   # scale so that the fit passes through the stated range at 1.0 s
        def Pclick(k):  # clicked centre (tracked) with scaled fit surface range
            return (np.linalg.norm(C(tcap(k)))-R)*s*ray(*tr[k])
        def Pfit(t):
            c=C(t); n=np.linalg.norm(c); return (n-R)*s*c/n
        out=[]
        # 38->39 (video 36->37)
        v3839=np.linalg.norm(Pclick(37)-Pclick(36))*25
        # 37->38: capture 37 dropped -> fit position projected (no click available); use fit for 37, click for 38
        v3738=np.linalg.norm(Pclick(36)-Pfit(1.48))*25
        vfit3839=np.linalg.norm(Pfit(1.56)-Pfit(1.52))*25; vfit3738=np.linalg.norm(Pfit(1.52)-Pfit(1.48))*25
        vinst=np.linalg.norm((p[3:6]+9.81*g*0.5))*s
        print(f'{cam} {ball} scale={s:.3f}: click 38-39={v3839:.2f} | 37-38={v3738:.2f} | fit 38-39={vfit3839:.2f} 37-38={vfit3738:.2f} inst(1.5)={vinst:.2f}  [note: G 38-39 straddles bounce, see green15]')
