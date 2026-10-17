import cv2, numpy as np, json
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work/'
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0311.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
lk=dict(winSize=(31,31),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,50,0.003))
def refine(f,p,r):
    x0,y0=int(round(p[0])),int(round(p[1]))
    P=f[y0-r:y0+r+1,x0-r:x0+r+1].astype(float)
    b,g,rr=P[...,0],P[...,1],P[...,2]
    w=np.clip(np.minimum(g,b)-90,0,None)
    yy,xx=np.mgrid[-r:r+1,-r:r+1]
    if w.sum()<1: return p, 0
    return (x0+(w*xx).sum()/w.sum(), y0+(w*yy).sum()/w.sum()), w.sum()
pts={'TLL':(1180.6,863.8),'TLR':(1409.4,817.0)}
out={}
for name,p48 in pts.items():
    pos={48:np.array(p48)}
    for rng in [range(49,72),range(47,20,-1)]:
        p=np.array(p48)
        for k in rng:
            prev=k-1 if rng.step==1 else k+1
            p1,st,err=cv2.calcOpticalFlowPyrLK(G[prev],G[k],np.float32(p).reshape(1,1,2),None,**lk)
            p=p1.reshape(2)
            # radius scaled by apparent size ~ disc radius ~ 7px at 48
            q,wsum=refine(fr[k],p,9)
            p=np.array(q); pos[k]=p
    out[name]={k:list(map(float,v)) for k,v in sorted(pos.items())}
json.dump(out,open(W+'taillights.json','w'))
for k in range(21,72):
    a=out['TLL'][k]; b=out['TLR'][k]
    print(k,np.round(a,2),np.round(b,2),round(np.hypot(b[0]-a[0],b[1]-a[1]),2))
