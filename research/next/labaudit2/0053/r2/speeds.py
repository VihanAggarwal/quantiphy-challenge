import numpy as np, json
f=711.;cx=640.;cy=360.
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
def nvec(p,r):
    p,r=np.radians(p),np.radians(r); return np.array([np.sin(r)*np.cos(p),-np.cos(r)*np.cos(p),-np.sin(p)])
T=json.load(open('bintrack.json'))
def cap(i): return i + (1 if i>=12 else 0) + (1 if i>=36 else 0)
R=np.array([ray(t['cx'],t['cy']) for t in T]); tc=np.array([cap(i) for i in range(48)])
P10=2.73*R[10]
for p,r in [(37,10),(34,13),(37.4,1.4)]:
    n=nvec(p,r); s=(n@P10)/(R@n); P=s[:,None]*R
    # along-track distance per capture frame
    d=np.linalg.norm(np.diff(P,axis=0),axis=1)/np.diff(tc)
    sp=d*25
    # smooth speeds in windows
    print(p,r,'speed per window (m/s):',' '.join(f'{tc[i]}:{sp[i-3:i+3].mean():.2f}' for i in range(3,45,4)))
    # quadratic fit of arc length
    arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))]
    k=np.polyfit(tc/25.,arc,2); print('   arc fit: v(0.4)=%.3f  accel=%.3f'%(2*k[0]*0.4+k[1],2*k[0]), ' fwd 10->11: %.3f'%(np.linalg.norm(P[11]-P[10])*25), 'click height',n@P10)
