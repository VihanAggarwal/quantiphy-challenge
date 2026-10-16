# Ballistic fit with the capture clock (25 fps, one dropped frame after video frame 11, so video n>=12 -> capture n+1)
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0020/scripts')
import json, numpy as np
from lm import least_squares
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
T=json.load(open(d+'tracks.json'))
CX=640.; CY=360.
def tau(n): n=np.asarray(n,float); return (n+(n>=12)+(n>=36))/25.
def downdir(vp,F):
    g=np.array([(vp[0]-CX)/F,(vp[1]-CY)/F,1.]); return g/np.linalg.norm(g)
def run(obj,frames,render,rng,F=711.,vp=(895.,1600.),gfree=False,wr=5.0,g=9.8):
    tr=T[render][obj]; fr=[f for f in frames if str(f) in tr]
    uv=np.array([tr[str(f)][:2] for f in fr]); t=tau(fr)
    gd0=downdir(vp,F)
    def pos(p,tt):
        dt=(np.asarray(tt)-0.6)[:,None]
        gd=gd0 if not gfree else np.array([p[6],p[7],1.])/np.linalg.norm([p[6],p[7],1.])
        return p[:3]+p[3:6]*dt+0.5*g*dt**2*gd
    def res(p):
        P=pos(p,t)
        r=np.c_[F*P[:,0]/P[:,2]+CX-uv[:,0],F*P[:,1]/P[:,2]+CY-uv[:,1]].ravel()
        if wr>0: r=np.r_[r,wr*(np.linalg.norm(p[:3])-rng)*100]
        return r
    u0=np.interp(0.6,t,uv[:,0]); v0=np.interp(0.6,t,uv[:,1])
    best=None
    for z in (1.5,2,2.5,3,3.5):
        ray=np.array([(u0-CX)/F,(v0-CY)/F,1.])
        p0=np.r_[z*ray,0,0,0]
        if gfree: p0=np.r_[p0,gd0[0]/gd0[2],gd0[1]/gd0[2]]
        s=least_squares(res,p0)
        if best is None or s.cost<best.cost: best=s
    p=best.x; P=pos(p,t)
    rms=np.sqrt(np.mean((np.c_[F*P[:,0]/P[:,2]+CX-uv[:,0],F*P[:,1]/P[:,2]+CY-uv[:,1]])**2))
    Q=pos(p,[0.6,0.64,0.8])
    fd=np.linalg.norm(Q[1]-Q[0])*25*100; inst=np.linalg.norm(p[3:6])*100; disp=np.linalg.norm(Q[2]-Q[0])*100
    gd=gd0 if not gfree else np.array([p[6],p[7],1.])/np.linalg.norm([p[6],p[7],1.])
    return dict(rms=rms,r06=np.linalg.norm(Q[0]),r08=np.linalg.norm(Q[2]),fd=fd,inst=inst,disp=disp,gd=gd)
if __name__=='__main__':
    jarF=list(range(14,28)); toyF=[14,15,16,17,19,20,21,22,23,24]
    for render in ('o','x','s'):
        for obj,fr,rng in (('jar',jarF if render!='s' else list(range(14,27)),1.9735),('toy',toyF,2.63)):
            for F in (711.,722.):
                for gfree in (False,True):
                    for wr in (0.,5.):
                        r=run(obj,fr,render,rng,F=F,gfree=gfree,wr=wr)
                        print('%s %s F=%d gfree=%d anchor=%d rms %.2f r0.6 %.3f r0.8 %.3f | fd v(0.6) %.1f inst %.1f | disp %.1f | gdir %s'%(render,obj,F,gfree,wr>0,r['rms'],r['r06'],r['r08'],r['fd'],r['inst'],r['disp'],np.round(r['gd'],2)))
