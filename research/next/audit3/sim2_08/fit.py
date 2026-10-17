import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_08')
from util import *
cfg={'0257':(9,range(3,12)), '0258':(11,range(8,16)), '0259':(9,range(3,15)), '0260':(10,range(6,16))}
v=sys.argv[1]; tf,rng=cfg[v]
fr=frames(v)
last=cv2.GaussianBlur(fr[-1],(3,3),0).astype(int)
def blob(n, xc=None):
    f=cv2.GaussianBlur(fr[n],(3,3),0).astype(int)
    d=np.abs(f-last).sum(axis=2)
    m=(d>60).astype(np.uint8); m[800:,:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    c=[i for i in range(1,nl) if st[i][4]>80]
    if xc is not None: c=[i for i in c if abs(st[i][0]+st[i][2]/2-xc)<60]
    i=max(c,key=lambda i:st[i][4])
    return st[i]
x,y,w,h,a=blob(tf)
pad=3
T=cv2.cvtColor(fr[tf],cv2.COLOR_BGR2GRAY)[y-pad:y+h+pad, x-pad:x+w+pad].astype(np.float32)
xc=x+w/2
ys=[];ns=[];tops=[];bots=[]
for n in rng:
    G=cv2.cvtColor(fr[n],cv2.COLOR_BGR2GRAY).astype(np.float32)
    x0=int(xc-w/2-60); 
    R=cv2.matchTemplate(G[:, x0:x0+w+120+2*pad], T, cv2.TM_CCOEFF_NORMED)
    _,mx,_,loc=cv2.minMaxLoc(R)
    j=loc[1]
    off=0
    if 0<j<R.shape[0]-1:
        a_,b_,c_=R[j-1,loc[0]],R[j,loc[0]],R[j+1,loc[0]]; off=0.5*(a_-c_)/(a_-2*b_+c_)
    ys.append(j+off+pad); ns.append(n)
    bx,by,bw,bh,_=blob(n,xc); tops.append(by); bots.append(by+bh)
    print(n, round(j+off,2), round(mx,3), 'blob top/bot', by, by+bh)
ns=np.array(ns,float); ys=np.array(ys)
for name,arr in [('tmpl',ys),('top',np.array(tops,float)),('bot',np.array(bots,float))]:
    p=np.polyfit(ns,arr,2); res=arr-np.polyval(p,ns)
    a2=2*p[0]; n0=-p[1]/(2*p[0])
    s=9.8/(a2*900)
    v6=9.8*(6-n0-0.5)/30; v12=9.8*(12-n0-0.5)/30
    print(f'{name}: a={a2:.3f} px/fr2 n0={n0:.2f} s={s*1e3:.4f}e-3 rms={res.std():.2f} v0.2={v6:.3f} v0.4={v12:.3f}')
