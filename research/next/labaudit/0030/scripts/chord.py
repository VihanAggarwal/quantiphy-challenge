import numpy as np, json
f=711.; c=np.array([640.,360.])
T2=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/track2.json'))
tA=np.array([0.2,0.4,0.6,0.8]); rA=np.array([0.8715,1.1660,1.3720,1.3150])
def u(x,y):
    v=np.array([(x-c[0])/f,(y-c[1])/f,1.]); return v/np.linalg.norm(v)
for r in ['s','o']:
    tr=T2[r]
    xs=np.array([t['cx'] for t in tr[:24]]); ys=np.array([t['cy'] for t in tr[:24]])
    for fps in [24,25]:
        P=[]
        for tq,rq in zip(tA,rA):
            fr=tq*fps
            x=np.interp(fr,np.arange(24),xs); y=np.interp(fr,np.arange(24),ys)
            P.append(rq*u(x,y))
        P=np.array(P)
        ch=np.linalg.norm(np.diff(P,axis=0),axis=1)/0.2*100
        print(r,'frame-of-t at',fps,'fps; anchor pts (cm):',np.round(P*100,1).tolist(),' chord speeds 0.2-0.4,0.4-0.6,0.6-0.8:',np.round(ch,1))
