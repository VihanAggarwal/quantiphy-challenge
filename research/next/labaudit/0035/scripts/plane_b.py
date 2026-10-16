import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0035/scripts')
from recon import *
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
n=np.array([-0.1146,-0.8224,-0.5573]); n/=np.linalg.norm(n)   # up normal (camera coords, y down)
trx=load('bx'); trs=json.load(open(f'{S}/tr_bs.json')); trs={k:{int(i):d for i,d in trs[k].items()} for k in trs}
def pix(tr,key,t):
    x=t*24; i0=int(np.floor(x)); a=x-i0; d=tr[key]
    return (1-a)*d[i0]['cx']+a*d[i0+1]['cx'],(1-a)*d[i0]['cy']+a*d[i0+1]['cy']
Rb,Rs=0.116,0.0905
# camera height above floor from each stated point (centre-range = stated + R, or stated as-is)
for conv in ['surface','centre']:
    for t,key,r in [(0.9,'sb',2.477),(0.9,'bb',2.7777),(1.4,'bb',2.602),(1.4,'sb',2.373)]:
        R=Rb if key=='bb' else Rs
        rc=r+R if conv=='centre' else r
        P=rc*ray(*pix(trx,key,t))
        H=-(n@P)+R   # height of camera above floor
        print(conv,t,key,'camera height above floor %.3f'%H)
H=1.785
def onplane(u,v,R):
    r=ray(u,v); t=-(H-R)/(n@r); return t*r
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)
T={k:orig(k)/25.0 for k in range(49)}
sizeD={'bb':0.232,'sb':0.181}
for src,tr in [('bx',trx),('bs',trs)]:
    P={key:{k:onplane(d['cx'],d['cy'],Rb if key=='bb' else Rs) for k,d in tr[key].items()} for key in ['bb','sb']}
    # add soccer rest from bx run
    if 0 not in P['sb']: P['sb'][9]=onplane(436.5,685.7,Rs)
    def at(key,t):
        x=t*24; i0=int(np.floor(x)); a=x-i0; return (1-a)*P[key][i0]+a*P[key][i0+1]
    def vfit(key,k,h=2):
        ks=[j for j in range(k-h,k+h+1) if j in P[key]]
        tt=np.array([T[j] for j in ks]); X=np.array([P[key][j] for j in ks]); return np.linalg.norm(np.polyfit(tt,X,1)[0])
    def vfwd(key,k): return np.linalg.norm(P[key][k+1]-P[key][k])/(T[k+1]-T[k])
    print('==',src)
    for t in [0.9,1.3,1.4]:
        k=int(round(t*24))
        print(' t=%.1f k%d sb fwd %.0f fit %.0f | bb fwd %.0f fit %.0f'%(t,k,100*vfwd('sb',k),100*vfit('sb',k),100*vfwd('bb',k),100*vfit('bb',k)))
    p0=P['bb'][9]; p1=at('bb',0.9)
    print(' bb disp rest(k9)->0.9s %.1f ; ->k22 %.1f ; ->k21 %.1f'%(100*np.linalg.norm(p1-p0),100*np.linalg.norm(P['bb'][22]-p0),100*np.linalg.norm(P['bb'][21]-p0)))
    s0=onplane(436.5,685.7,Rs)
    if 21 in P['sb'] and 22 in P['sb']:
        print(' sb disp rest->0.9s %.1f ; ->k22 %.1f'%(100*np.linalg.norm(at('sb',0.9)-s0),100*np.linalg.norm(P['sb'][22]-s0)))
    print(' ranges: bb rest %.3f, bb 0.9 %.3f, sb rest %.3f, sb 0.9 %.3f'%(np.linalg.norm(p0),np.linalg.norm(p1),np.linalg.norm(s0),np.linalg.norm(at('sb',0.9))))
