import numpy as np
f=711.0; cx,cy=640.,360.
def ray(u,v):
    r=np.array([(u-cx)/f,(v-cy)/f,1.]); return r/np.linalg.norm(r)
Pt,Pb,e,h,n=np.load('model.npy')
r=0.0325; P0=Pb+r*n
def b3(u,v):
    R=ray(u,v); return (n@P0)/(n@R)*R
# centroids (s render, board-restricted) frames 12-16
tr={12:(545.4,330.1),13:(546.2,341.5),14:(547.2,354.7),15:(548.1,370.8),16:(549.4,389.8)}
P={k:b3(*v) for k,v in tr.items()}
s={k:(P[k]-P[12])@e for k in P}
for k in sorted(P): print(k,'range %.4f'%np.linalg.norm(P[k]),'s_along %.2f cm'%(100*s[k]))
ks=sorted(P)
for a,b in zip(ks[:-1],ks[1:]):
    d=np.linalg.norm(P[b]-P[a])
    print('%d->%d  |dP|=%.2f cm  v24=%.1f cm/s  v25=%.1f cm/s'%(a,b,100*d,100*d*24,100*d*25))
t=np.array(ks)/24.; S=np.array([s[k] for k in ks])
c=np.polyfit(t,S,2); print('quad fit a=%.2f m/s2'%(2*c[0]),'v(0.6)=%.1f cm/s'%(100*(2*c[0]*0.6+c[1])), 'resid cm',np.round(100*(np.polyval(c,t)-S),2))
print('t0 (v=0) = %.3f s'%(-c[1]/(2*c[0])))
