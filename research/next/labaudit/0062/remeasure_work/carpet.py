import cv2, numpy as np
from lm import lsq
g=cv2.cvtColor(cv2.imread('median_bg.png'),cv2.COLOR_BGR2GRAY).astype(np.float32)
f=711.;cx=640.;cy=360.
Kinv=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1]]))
gx=cv2.Sobel(g,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)
# carpet polygon mask (exclude walls, objects, cables region roughly)
mask=np.zeros(g.shape,np.uint8)
poly=np.array([[150,300],[600,240],[800,260],[960,330],[1100,470],[1000,560],[1200,700],[150,700]])
cv2.fillPoly(mask,[poly],1)
# exclude objects: box, mario, bag, board area (median bg board blurred), tape strips
for (x,y,w,h) in [(480,450,90,100),(560,560,160,120),(760,280,150,110),(600,380,130,50),(840,640,160,80),(1020,680,260,40)]:
    mask[y:y+h,x:x+w]=0
P=[];T=[];W=[]
S=48
for y in range(250,700-S,S//2):
    for x in range(150,1150-S,S//2):
        if mask[y:y+S,x:x+S].mean()<0.98: continue
        a=gx[y:y+S,x:x+S]; b=gy[y:y+S,x:x+S]
        Jxx=(a*a).sum(); Jyy=(b*b).sum(); Jxy=(a*b).sum()
        lam1=0.5*(Jxx+Jyy+np.sqrt((Jxx-Jyy)**2+4*Jxy**2)); lam2=0.5*(Jxx+Jyy-np.sqrt((Jxx-Jyy)**2+4*Jxy**2))
        coh=(lam1-lam2)/(lam1+lam2+1e-9)
        th=0.5*np.arctan2(2*Jxy,Jxx-Jyy)+np.pi/2  # stripe direction (perp to gradient)
        P.append((x+S/2,y+S/2)); T.append(th); W.append(coh)
P=np.array(P);T=np.array(T);W=np.array(W)
print('patches',len(P),'mean coherence',round(W.mean(),3))
def resid(vp):
    d=np.c_[vp[0]-P[:,0],vp[1]-P[:,1]]; ang=np.arctan2(d[:,1],d[:,0])
    e=np.angle(np.exp(2j*(ang-T)))/2
    return e*np.sqrt(W)
# init guess: try grid of VP far away
best=None
for X in np.linspace(-20000,20000,81):
    for Y in np.linspace(-6000,2000,41):
        r=resid((X,Y)); c=r@r
        if best is None or c<best[0]: best=(c,X,Y)
vp,r=lsq(resid,[best[1],best[2]],huber=0.1)
print('carpet VP',np.round(vp,1),'rms rad',round(float(np.sqrt(np.mean((r/np.sqrt(W))**2))),4))
ds=Kinv@np.r_[vp,1]; ds/=np.linalg.norm(ds)
dc=np.load('dc.npy')
print('carpet dir',np.round(ds,4),'angle to corridor deg',round(float(np.degrees(np.arccos(abs(ds@dc)))),2))
nb=np.load('n_fit_711.npy')[:3]; ns=np.load('n_seams.npy')
print('n_board.ds',round(float(nb@ds),4),'deg',round(float(np.degrees(np.arcsin(abs(nb@ds)))),2))
print('n_seams.ds',round(float(ns@ds),4),'deg',round(float(np.degrees(np.arcsin(abs(ns@ds)))),2))
n2=np.cross(dc,ds); n2/=np.linalg.norm(n2); n2=n2 if n2[1]>0 else -n2
print('n from corridor x carpet',np.round(n2,4),'angle to n_board',round(float(np.degrees(np.arccos(n2@nb))),2),'to n_seams',round(float(np.degrees(np.arccos(n2@ns))),2))
np.save('n_cc.npy',n2)
# residual by region
e=resid(vp)/np.sqrt(W)
for lab,sel in [('top',P[:,1]<400),('mid',(P[:,1]>=400)&(P[:,1]<550)),('bot',P[:,1]>=550)]:
    print(lab,sel.sum(),'mean resid deg',round(float(np.degrees(np.mean(e[sel]))),2))
