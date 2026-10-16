import json, numpy as np, sys
sys.path.insert(0,"/home/user/quantiphy-challenge/research/next/labaudit/0020/scripts"); from lm import least_squares
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
T=json.load(open(d+'tracks.json'))
F=711.; CX=640.; CY=360.
vp=np.array([895.,1600.])
down=np.array([(vp[0]-CX)/F,(vp[1]-CY)/F,1.]); down/=np.linalg.norm(down)
FPS=float(sys.argv[1]) if len(sys.argv)>1 else 24.
G=9.8
def proj(P):
    return np.c_[F*P[:,0]/P[:,2]+CX, F*P[:,1]/P[:,2]+CY]
def model(p,t,gdir,g=G):
    A=p[:3]; B=p[3:6]; dt=(t-0.6)[:,None]
    return A+B*dt+0.5*g*dt**2*gdir
def fit(obj,frames,render='o',rng=None,w_r=0.0,gdir=down,g=G,fps=FPS):
    tr=T[render][obj]
    fr=[f for f in frames if str(f) in tr]
    uv=np.array([tr[str(f)][:2] for f in fr]); t=np.array(fr)/fps
    def res(p):
        r=(proj(model(p,t,gdir,g))-uv).ravel()
        if w_r>0:
            r=np.r_[r, w_r*(np.linalg.norm(p[:3])-rng)*100]
        return r
    # init: point along ray at 0.6s
    f0=0.6*fps
    u0=np.interp(f0,fr,uv[:,0]); v0=np.interp(f0,fr,uv[:,1])
    best=None
    for z0 in (1.5,2.0,2.5,3.0,4.0):
        A=z0*np.array([(u0-CX)/F,(v0-CY)/F,1.])
        p0=np.r_[A,0,0,0]
        s=least_squares(res,p0)
        if best is None or s.cost<best.cost: best=s
    p=best.x
    rr=proj(model(p,t,gdir,g))-uv
    return p,np.sqrt(np.mean(rr**2)),fr
def report(name,p,fps=FPS,g=G,gdir=down):
    A=p[:3];B=p[3:6]
    P08=model(p,np.array([0.8]),gdir,g)[0]
    print('%s range(0.6)=%.3f  speed(0.6)=%.1f cm/s  disp(0.6->0.8)=%.1f cm  range(0.8)=%.3f  vel=%s'%(name,np.linalg.norm(A),np.linalg.norm(B)*100,np.linalg.norm(P08-A)*100,np.linalg.norm(P08),np.round(B,2)))
if __name__=='__main__':
    jarF=list(range(15,28)); toyF=[14,15,16,17,19,20,21,22,23,24]
    for render in ('o','s','x'):
        print('== render',render,'fps',FPS)
        p,rms,_=fit('jar',jarF,render); print('jar free  rms %.2f px'%rms,end='  '); report('jar',p)
        p,rms,_=fit('jar',jarF,render,rng=1.9735,w_r=5); print('jar +range rms %.2f px'%rms,end='  '); report('jar',p)
        p,rms,_=fit('toy',toyF,render); print('toy free  rms %.2f px'%rms,end='  '); report('toy',p)
        p,rms,_=fit('toy',toyF,render,rng=2.63,w_r=5); print('toy +range rms %.2f px'%rms,end='  '); report('toy',p)
