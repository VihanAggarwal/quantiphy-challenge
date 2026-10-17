import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
v=sys.argv[1]
c=cv2.VideoCapture(D+v+'.mp4'); G=[]
while True:
    ok,f=c.read()
    if not ok: break
    G.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)[800:940,400:1000])
G=np.array(G,np.float32); bg=np.median(G,0)
masks=[((bg-g)>30)&(g<70) for g in G]
masks=[m.astype(np.float32) for m in masks]
def best_shift(a,b):
    A=np.fft.rfft2(a); B=np.fft.rfft2(b)
    cc=np.fft.irfft2(np.conj(A)*B, s=a.shape)
    iy,ix=np.unravel_index(np.argmax(cc),cc.shape); peak=cc[iy,ix]
    l=cc[iy,(ix-1)%cc.shape[1]]; r=cc[iy,(ix+1)%cc.shape[1]]
    sub=0.5*(l-r)/(l-2*peak+r)
    dx=ix+sub
    if dx>cc.shape[1]/2: dx-=cc.shape[1]
    return dx, peak/np.sqrt((a*a).sum()*(b*b).sum())
N=len(masks); R=[]
for i in range(N):
    for j in range(i+30,N):
        dx,nc=best_shift(masks[i],masks[j]); R.append((i,j,dx,nc,dx/(j-i)))
R=np.array(R)
top=R[R[:,3]>=np.quantile(R[:,3],0.9)]
print(v,'n',len(top),'median px/frame %.4f'%np.median(top[:,4]),'std %.4f'%top[:,4].std())
# centroid linear fit
cx=[]; 
for m in masks:
    ys,xs=np.nonzero(m); cx.append(xs.mean())
p=np.polyfit(np.arange(N),cx,1); print(v,'centroid fit px/frame %.4f'%p[0])
