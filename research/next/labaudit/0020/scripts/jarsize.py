import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0020/scripts')
import cv2, numpy as np, json
import ballfit2 as BF
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
T=json.load(open(d+'tracks.json'))
F=711.
# ranges per frame from the anchored, VP-gravity fit (o render)
jarF=list(range(14,28))
def ranges(render):
    tr=T[render]['jar']; fr=[f for f in jarF if str(f) in tr]
    uv=np.array([tr[str(f)][:2] for f in fr]); t=BF.tau(fr)
    out={}
    r=BF.run('jar',jarF,render,1.9735)
    return r
# refit to get positions per frame: replicate quickly
from lm import least_squares
def fitpos(render,F=711.):
    tr=T[render]['jar']; fr=[f for f in jarF if str(f) in tr]
    uv=np.array([tr[str(f)][:2] for f in fr]); t=BF.tau(fr)
    gd=BF.downdir((895.,1600.),F)
    def pos(p,tt):
        dt=(np.asarray(tt)-0.6)[:,None]; return p[:3]+p[3:6]*dt+0.5*9.8*dt**2*gd
    def res(p):
        P=pos(p,t); r=np.c_[F*P[:,0]/P[:,2]+640-uv[:,0],F*P[:,1]/P[:,2]+360-uv[:,1]].ravel()
        return np.r_[r,5*(np.linalg.norm(p[:3])-1.9735)*100]
    best=None
    for z in (1.5,2,2.5):
        u0,v0=uv[0]; s=least_squares(res,np.r_[z*np.array([(u0-640)/F,(v0-360)/F,1]),0,0,0])
        if best is None or s.cost<best.cost: best=s
    return {f:np.linalg.norm(pos(best.x,[BF.tau(f)])[0]) for f in range(12,30)}
R=fitpos('o')
def feret(xs,ys):
    P=np.c_[xs,ys].astype(np.float32)
    hull=cv2.convexHull(P).reshape(-1,2)
    angs=np.radians(np.arange(0,180,2)); ext=[]
    for a in angs:
        pr=hull@np.array([np.cos(a),np.sin(a)]); ext.append(pr.max()-pr.min())
    ext=np.array(ext); return ext.max(),ext.min()
print('frame range  | thr  maxF minF (px) -> cm max/min')
for i in [14,15,16,17,20,21,22,23,24,25]:
    im=cv2.imread(d+f'frames/0020_f{i:02d}.png')
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
    u,v=T['o']['jar'][str(i)][:2]
    line=f'f{i} r={R[i]:.3f} |'
    for vt in (170,190,210):
        m=((hsv[...,1]<55)&(hsv[...,2]>vt)).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        k=lab[int(round(v)),int(round(u))]
        if k==0:
            ds=[np.hypot(*(cen[j]-[u,v])) for j in range(1,n)]; k=1+int(np.argmin(ds))
        ys,xs=np.nonzero(lab==k)
        if len(xs)>5000: line+=f' v>{vt}: merged |'; continue
        mx,mn=feret(xs,ys)
        line+=f' v>{vt}: {mx:.0f}/{mn:.0f} -> {mx*R[i]/F*100:.1f}/{mn*R[i]/F*100:.1f} |'
    print(line)
