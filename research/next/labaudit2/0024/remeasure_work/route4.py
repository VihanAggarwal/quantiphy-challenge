# Book lying on the table at the end of 0024 (median frames 39-48): table plane from horizon VPs + board low edge scale
import cv2,numpy as np,sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work')
import rect
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
f=711.
def K1(u,v): return np.array([(u-640)/f,(v-360)/f,1.])
img=cv2.imread(f'{W}/captured_0024x_medB.png'); gr=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(float)
b,g,r=[img[...,i].astype(float) for i in range(3)]; br=b-r
back=[];front=[];bottom=[]
for x in range(515,612,3):
    col=gr[455:505,x]; bc=br[455:505,x]
    # top face rows: gray>185 and B-R>5
    tf=np.where((col>185)&(bc>5))[0]
    if len(tf)<5: continue
    t0=tf.min()
    # back edge: half crossing between value above (row t0-2) and plateau
    above=col[t0-2]; plat=np.median(col[t0+1:t0+5]); thr=(above+plat)/2
    yb=None
    for i in range(t0-3,t0+2):
        if (col[i]-thr)*(col[i+1]-thr)<=0 and col[i+1]!=col[i]: yb=i+(thr-col[i])/(col[i+1]-col[i]); break
    # front dark line: first local min below top-face block
    t1=tf[tf<t0+25].max() if True else None
    seg=col[t1:t1+5]; i=int(np.argmin(seg)); yf=t1+i
    if 0<i<4:
        den=seg[i-1]-2*seg[i]+seg[i+1]; yf=t1+i+(seg[i-1]-seg[i+1])/(2*den)
    # bottom dark: min in next 8..16 rows
    seg2=col[int(yf)+6:int(yf)+16]; j=int(np.argmin(seg2)); ybo=int(yf)+6+j
    if yb is not None:
        back.append((x,455+yb)); front.append((x,455+yf)); bottom.append((x,455+ybo))
back=np.array(back);front=np.array(front);bottom=np.array(bottom)
def fit(P):
    A=np.c_[P[:,0],np.ones(len(P))]
    for it in range(3):
        k,c=np.linalg.lstsq(A,P[:,1],rcond=None)[0]; res=P[:,1]-A@[k,c]; keep=np.abs(res)<max(0.7,2.5*res.std()); P=P[keep]; A=A[keep]
    return k,c,res.std(),len(P)
fb=fit(back);ff=fit(front);fbo=fit(bottom)
print('back',np.round(fb,3),'front(dark)',np.round(ff,3),'bottom(dark)',np.round(fbo,3))
# table plane normal from horizon through VPs
V1=np.array([1922.7,357.5,1.]);V2=np.array([167.2,351.3,1.])
l=np.cross(V1,V2); Kinv=np.array([[1/f,0,-640/f],[0,1/f,-360/f],[0,0,1]]); K=np.linalg.inv(Kinv)
n=K.T@l; n/=np.linalg.norm(n)
if n[1]<0: n=-n
print('table normal',np.round(n,4))
# scale: board low corners from board model (lowmid range 0.99)
rect.f=f
r_,P=rect.rect((606.6,467.5),(708.0,492.5),(862.7,361.5),(751.1,360.1),verbose=False); P=np.array(P)
s=0.99/np.linalg.norm((P[0]+P[1])/2); P=P*s
print('board LL,LR heights n.P',round(float(n@P[0]),4),round(float(n@P[1]),4))
for h in [float(n@P[0]+n@P[1])/2,0.155,0.17]:
  for frontdy in [0,-1.0]:
    def on(u,v,hh): rr=K1(u,v); return (hh/(n@rr))*rr
    xs=np.arange(525,605,5.)
    Pbot=np.array([on(x,fbo[0]*x+fbo[1],h) for x in xs])
    # front-face top edge at same 3D (x,z) as bottom edge but height T: estimate T from front line
    # use: top-front point lies on vertical (along -n) above bottom point: X = Pbot - T n ; project and match v
    Ts=[]
    for x,pb in zip(xs,Pbot):
        vt=ff[0]*x+ff[1]+frontdy
        # solve T such that projection of pb - T n has v = vt (approx ignore u shift)
        best=min(np.linspace(0,0.04,4001),key=lambda T:abs(((pb-T*n)[1]/(pb-T*n)[2])*f+360-vt)); Ts.append(best)
    T=float(np.median(Ts))
    Pf=np.array([on(x,ff[0]*x+ff[1]+frontdy,h-T) for x in xs]); Pb=np.array([on(x,fb[0]*x+fb[1],h-T) for x in xs])
    # line direction from front points, distance of back points to front line
    d=Pf[-1]-Pf[0]; d/=np.linalg.norm(d)
    dist=[np.linalg.norm(np.cross(pb-Pf[0],d)) for pb in Pb]
    print('h=%.4f frontdy=%.1f T=%.4f  W(dist back-line to front-line)=%.2f cm (spread %.2f)  front/back line angle %.1f deg'%(h,frontdy,T,np.mean(dist)*100,np.std(dist)*100,np.degrees(np.arccos(abs(d@((Pb[-1]-Pb[0])/np.linalg.norm(Pb[-1]-Pb[0])))))))
