import numpy as np, sys
from chord import solve_f
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/remeasure_work/'
v=sys.argv[1]; k0,k1=int(sys.argv[2]),int(sys.argv[3]); D1,D2,L=float(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6])
c=float(sys.argv[7]) if len(sys.argv)>7 else 480
o=np.loadtxt(W+'eagle_%s.txt'%v)
o=o[(o[:,0]>=k0)&(o[:,0]<=k1)&(o[:,7]>150)]
k=o[:,0]
for P in [24.0,25.5]:
  w=2*np.pi/P
  A=np.c_[np.ones_like(k),k,k**2,np.sin(w*k),np.cos(w*k)]
  cx=np.linalg.lstsq(A,o[:,1],rcond=None)[0]; cy=np.linalg.lstsq(A,o[:,2],rcond=None)[0]
  ev=lambda cc,t: cc[0]+cc[1]*t+cc[2]*t*t
  p1=(ev(cx,24),ev(cy,24)); p2=(ev(cx,48),ev(cy,48))
  rx=o[:,1]-A@cx; ry=o[:,2]-A@cy
  print('P',P,'p1',np.round(p1,1),'p2',np.round(p2,1),'rms',round(rx.std(),2),round(ry.std(),2),'f',round(solve_f(L,p1,p2,D1,D2,(c,c)),1))
