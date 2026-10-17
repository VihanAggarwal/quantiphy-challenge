import cv2, numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work')
from recon import *
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0311.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
lk=dict(winSize=(41,41),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,50,0.003))
def yellow(f,p,r=7):
    x0,y0=int(round(p[0])),int(round(p[1]))
    P=f[y0-r:y0+r+1,x0-r:x0+r+1].astype(float)
    b,g,rr=P[...,0],P[...,1],P[...,2]
    w=np.clip(np.minimum(rr,g)-b-15,0,None)
    yy,xx=np.mgrid[-r:r+1,-r:r+1]
    if w.sum()<15: return None
    return np.array([x0+(w*xx).sum()/w.sum(), y0+(w*yy).sum()/w.sum()])
out={}
for name,p48 in {'RW':(1111.6,890.0),'FW':(933.0,752.4)}.items():
    q=yellow(fr[48],p48); pos={48:q}
    for rng in [range(49,72),range(47,10,-1)]:
        p=q.copy()
        for k in rng:
            prev=k-1 if rng.step==1 else k+1
            p1,st,err=cv2.calcOpticalFlowPyrLK(G[prev],G[k],np.float32(p).reshape(1,1,2),None,**lk)
            pp=p1.reshape(2); y=yellow(fr[k],pp)
            if y is None or not st[0]: break
            p=y; pos[k]=p
    out[name]={k:list(map(float,v)) for k,v in sorted(pos.items())}
    print(name,min(pos),max(pos))
json.dump(out,open(W+'hubs.json','w'))
for f in [4100,4240,4380]:
    K,Ki,D,L,U=cam(f)
    TL=json.load(open(W+'taillights.json'))
    QL,_=tri({int(k):v for k,v in TL['TLL'].items() if int(k)>=22},f)
    QR,_=tri({int(k):v for k,v in TL['TLR'].items() if int(k)>=31},f)
    O=(QL+QR)/2
    res={}
    for nm in ['RW','FW']:
        tr={int(k):v for k,v in out[nm].items()}
        Q,r=tri(tr,f); d=Q-O; res[nm]=d
        print(f,nm,'reproj rms %.2f'%r,'fwd %.4f lat %.4f up %.4f'%(d@D,d@L,d@U),'n',len(tr))
    print('  wheelbase(V-units) %.4f  TLsep %.4f  WB/TLsep %.3f'%((res['FW']-res['RW'])@D,np.linalg.norm(QL-QR),((res['FW']-res['RW'])@D)/np.linalg.norm(QL-QR)), 'hub up diff', (res['FW']-res['RW'])@U)
