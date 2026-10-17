import cv2, numpy as np, sys
vid = sys.argv[1]; init=sys.argv[2]; out=sys.argv[3]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
N=len(fr)
t0=np.loadtxt(init,delimiter=',')
def fit_circle(x,y):
    A=np.c_[2*x,2*y,np.ones_like(x)]
    b=x**2+y**2
    sol,*_=np.linalg.lstsq(A,b,rcond=None)
    cx,cy=sol[0],sol[1]; r=np.sqrt(sol[2]+cx**2+cy**2)
    return cx,cy,r
ang=np.linspace(0,2*np.pi,720,endpoint=False)
rad=np.arange(40,80,0.25)
res=[]
for i in range(N):
    img=cv2.GaussianBlur(fr[i].astype(np.float32),(0,0),1.0)
    cx,cy=t0[i,5],t0[i,6]
    for it in range(3):
        X=cx+np.cos(ang)[:,None]*rad[None,:]
        Y=cy+np.sin(ang)[:,None]*rad[None,:]
        prof=cv2.remap(img,X.astype(np.float32),Y.astype(np.float32),cv2.INTER_LINEAR).sum(2)
        dprof=np.diff(prof,axis=1)  # outward derivative
        # inside brighter: most negative derivative
        j=np.argmin(dprof,axis=1)
        strength=-dprof[np.arange(len(ang)),j]
        # subpixel parabola
        jj=np.clip(j,1,dprof.shape[1]-2)
        a=dprof[np.arange(len(ang)),jj-1]; b=dprof[np.arange(len(ang)),jj]; cc=dprof[np.arange(len(ang)),jj+1]
        den=a-2*b+cc; off=np.where(np.abs(den)>1e-6,0.5*(a-cc)/den,0)
        r_e=rad[0]+(jj+0.5+np.clip(off,-1,1))*(rad[1]-rad[0])
        px=cx+np.cos(ang)*r_e; py=cy+np.sin(ang)*r_e
        keep=strength>0.3*np.median(strength)
        fx,fy,fr_=fit_circle(px[keep],py[keep])
        for _ in range(4):
            d=np.abs(np.hypot(px-fx,py-fy)-fr_)
            k2=keep&(d<max(1.0,2.5*np.median(d[keep])))
            fx,fy,fr_=fit_circle(px[k2],py[k2])
        cx,cy=fx,fy
    res.append((i,fx,fy,2*fr_,k2.mean(),np.median(strength)))
    print('%d %.2f %.2f D=%.2f inl=%.2f str=%.0f'%res[-1])
np.savetxt(out,np.array(res),fmt='%.4f',delimiter=',',header='i,x,y,D,inlier,strength')
