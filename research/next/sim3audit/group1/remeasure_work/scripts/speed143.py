import numpy as np
yh=540.; cx=960.
F=[(0,946,836),(12,790,824),(24.6,717,793),(36.8,654,766),(49.3,720,736),(61.8,769,712.5),(74,820,692),(86.5,777,682),(99,739,673)]
t=np.array([f[0] for f in F])
def traj(K,Hc):
    return np.array([[(x-cx)*Hc/(y-yh), K/(y-yh)] for _,x,y in F])
for K,Hc in [(2393,1.286),(2440,1.286),(2340,1.286),(2393,1.26),(1250,1.286)]:
    P=traj(K,Hc)
    seg=np.hypot(*np.diff(P,axis=0).T)/np.diff(t)*24
    # local quadratic fits (3 points) derivative at 24 and 48
    out=[]
    for tq in (24,48):
        k=np.argsort(np.abs(t-tq))[:4]; k=np.sort(k)
        px=np.polyfit(t[k],P[k,0],2); pz=np.polyfit(t[k],P[k,1],2)
        v=np.hypot(np.polyval(np.polyder(px),tq),np.polyval(np.polyder(pz),tq))*24
        out.append(round(v,2))
    # also 5-frame centred chord along a cubic spline through all points
    print('K',K,'Hc',Hc,'seg speeds',np.round(seg,2),' v(24),v(48) quad4:',out)
# heading (deg from +Z) per segment in K=2393 world
P=traj(2393,1.286); d=np.diff(P,axis=0); print('headings',np.round(np.degrees(np.arctan2(d[:,0],d[:,1])),1))
