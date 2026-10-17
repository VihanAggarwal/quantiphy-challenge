import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
v=sys.argv[1]
c=cv2.VideoCapture(D+v+'.mp4'); G=[]
while True:
    ok,f=c.read()
    if not ok: break
    G.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)[480:620,380:1400].astype(np.float32))
G=np.array(G); N=len(G)
masks=[(g<45).astype(np.float32) for g in G]
def best_shift(a,b):
    A=np.fft.rfft2(a); B=np.fft.rfft2(b)
    cc=np.fft.irfft2(np.conj(A)*B, s=a.shape)
    iy,ix=np.unravel_index(np.argmax(cc),cc.shape); peak=cc[iy,ix]
    l=cc[iy,(ix-1)%cc.shape[1]]; r=cc[iy,(ix+1)%cc.shape[1]]
    dx=ix+0.5*(l-r)/(l-2*peak+r)
    if dx>cc.shape[1]/2: dx-=cc.shape[1]
    dy=iy if iy<cc.shape[0]/2 else iy-cc.shape[0]
    return dx,dy, peak/np.sqrt((a*a).sum()*(b*b).sum())
R=[]
for i in range(N):
    for j in range(i+30,N):
        dx,dy,nc=best_shift(masks[i],masks[j]); R.append((i,j,dx,dy,nc,dx/(j-i)))
R=np.array(R); top=R[R[:,4]>=np.quantile(R[:,4],0.9)]
print(v,'gait-matched px/frame median %.4f std %.4f  dy med %.2f'%(np.median(top[:,5]),top[:,5].std(),np.median(top[:,3])))
cx=[np.nonzero(m)[1].mean() for m in masks]; print('centroid fit %.4f'%np.polyfit(np.arange(N),cx,1)[0], 'area',np.mean([m.sum() for m in masks]))
# joint pitch: median bg over frames, column profile in the band just above the pool edge
bg=np.median(G,0)
sm=lambda a,k: np.convolve(np.pad(a,k//2,mode="edge"),np.ones(k)/k,mode="valid")
c2=cv2.VideoCapture(D+v+'.mp4'); ok,f=c2.read(); g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32)
# find pool edge row
colprof=g[560:700,800:1800].mean(1); 
d=np.diff(colprof); ye=560+np.argmin(d); print('pool edge row (max drop) ~',ye)
for (y0,y1) in [(ye-60,ye-25),(ye-20,ye-3),(300,420)]:
    band=g[y0:y1,:].mean(0); hp=band-sm(band,31)
    mins=[x for x in range(5,1915) if hp[x]==hp[x-5:x+6].min() and hp[x]<-10]
    sub=[x+0.5*(hp[x-1]-hp[x+1])/(hp[x-1]-2*hp[x]+hp[x+1]) for x in mins]
    print('band',y0,y1,' '.join('%.1f'%s for s in sub)); print('  diffs',np.round(np.diff(sub),1))
