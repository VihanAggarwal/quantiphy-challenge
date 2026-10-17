# Joint fit: rolling on the table (centre 2 cm up) then free fall after the centre passes the near edge (y_table = ye).
import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0033/scripts')
from geo import *
def model(p, cs, P, ye=0.0, g=980.):
    x0,y0,vx,vy=p  # table coords at c35, cm and cm/frame
    out=[]
    for c in cs:
        dt=c-35
        x=x0+vx*dt; y=y0+vy*dt; z=2.0
        te=(ye-y0)/vy  # frames after c35 when centre passes edge
        if dt>te:
            tf=(dt-te)/25.; z=2.0-0.5*g*tf**2
        Xt=np.array([x,y,z]); Xc=P['R']@Xt+P['t']
        out.append(Xc)
    return np.array(out)
def run(R='x',f=711,use=(31,32,33,34,35,36,38),key=('wcx','wcy'),ye=0.0,wts=None):
    P=pose(f); T=load_track(R)
    inv={cap(k):k for k in T}
    cs=list(use); uv=np.array([[T[inv[c]][key[0]],T[inv[c]][key[1]]] for c in cs])
    def res(p): return (project(model(p,cs,P,ye),f)-uv).ravel()
    s=least_squares(res,[15.,8.,-1.5,-5.])
    return s,P,cs,uv
if __name__=='__main__':
    for R in ['x','s']:
      for f in [711,740]:
        for use in [(31,32,33,34,35,36,38),(33,34,35,36,38),(31,32,33,34,35)]:
          s,P,cs,uv=run(R,f,use)
          p=s.x; te=35+(0-p[1])/p[3]
          pr=project(model(p,[35,36,37,38,39],P),f)
          print(R,f,use,'vx,vy cm/s %.1f %.1f |v| %.1f  edge at c%.2f'%(p[2]*25,p[3]*25,np.hypot(p[2],p[3])*25,te),
                'res',np.round(s.fun.reshape(-1,2),1).tolist())
          print('    pred c35..39',np.round(pr,0).tolist())
