# Arc 2 (bounce 1 -> bounce 2): ballistic fit with the launch point ON the table (centre 2 cm up) at time tb1,
# g = 980 cm/s^2 along the table normal, plane scale from the table. Compare the range at t = 0.9 s (c22.5)
# with the stated ToF 1.457 m, to learn the ToF/plane ratio for the ball in flight.
import numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0033/scripts')
from geo import *
for R in ['x','s']:
  T=load_track(R)
  Cp=json.load(open(BASE+'capsule_%s.json'%R)) if R=='x' else None
  for f in [711,740]:
    P=pose(f)
    ks=list(range(KS0,KS1)); cs=np.array([cap(k) for k in ks],float)
    uv=np.array([Cp[str(k)]['mid'] if Cp else [T[k]['cx'],T[k]['cy']] for k in ks])
    for gscale in [1.0]:
      g=980.
      def traj(p,c):
        tb,bx,by,vx,vy,vz=p
        dt=(np.atleast_1d(c)-tb)/25.
        x=bx+vx*dt; y=by+vy*dt; z=2+vz*dt-0.5*g*dt**2
        Xt=np.stack([x,y,z],1); return (P['R']@Xt.T).T+P['t']
      def res(p): return (project(traj(p,cs),f)-uv).ravel()
      best=None
      for y0 in [40,60,80]:
        for vy0 in [-50,-100,0]:
          s=least_squares(res,[15.6,25.,y0,0.,vy0,200.])
          if best is None or s.cost<best.cost: best=s
      p=best.x; rms=np.sqrt(np.mean(best.fun**2))
      tb2=p[0]+2*p[5]/g*25
      X225=traj(p,22.5)[0]; Xb1=traj(p,p[0])[0]; Xb2=traj(p,tb2)[0]
      print('%s f%d rms %.2f px  tb1 c%.2f tb2 c%.2f  vy %.0f vz %.0f cm/s | range b1 %.1f  c22.5 %.1f (surface %.1f)  b2 %.1f | ToF/plane at c22.5 = %.3f | b2 image %s'%(
            R,f,rms,p[0],tb2,p[4],p[5],np.linalg.norm(Xb1),np.linalg.norm(X225),np.linalg.norm(X225)-2,np.linalg.norm(Xb2),145.7/(np.linalg.norm(X225)-2),np.round(project(Xb2[None],f)[0],0)))
