import numpy as np, json
T=json.load(open('track.json'))
t=np.array([r['i'] for r in T],float); x=np.array([r['cx'] for r in T]); y=np.array([r['cy'] for r in T])
xb=np.array([(r['x0']+r['x1'])/2 for r in T])
def fit(t,z,P,deg=3,K=2):
    w=2*np.pi/P; cols=[t**k for k in range(deg+1)]
    for k in range(1,K+1): cols+= [np.cos(k*w*t),np.sin(k*w*t)]
    A=np.stack(cols,1); c,res,_,_=np.linalg.lstsq(A,z,rcond=None)
    sm=np.stack([t**k for k in range(deg+1)],1)@c[:deg+1]
    return sm, np.sqrt(np.mean((A@c-z)**2))
for P in [16.5,17,17.2,17.5,18]:
    sx,rx=fit(t,x,P); sy,ry=fit(t,y,P); print(P, 'rms',round(rx,2),round(ry,2))
P=17.2
sx,_=fit(t,x,P); sy,_=fit(t,y,P)
for deg in [2,3,4]:
    a,_=fit(t,x,P,deg); b,_=fit(t,y,P,deg)
    print('deg',deg,'x0,x24',a[0].round(1),a[24].round(1),'y0,y24',b[0].round(1),b[24].round(1),'x41',a[41].round(1),'x58',a[58].round(1))
np.save('smooth.npy',np.stack([sx,sy]))
print('smooth x', sx[::4].round(1)); print('smooth y', sy[::4].round(1))
print('vx px/frame', np.diff(sx)[::4].round(2))
