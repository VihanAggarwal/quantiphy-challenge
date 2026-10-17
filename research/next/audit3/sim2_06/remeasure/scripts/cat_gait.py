import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
v=sys.argv[1]; thr=int(sys.argv[2]) if len(sys.argv)>2 else 60
c=cv2.VideoCapture(D+v+'.mp4'); G=[]
while True:
    ok,f=c.read()
    if not ok: break
    G.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)[800:940,400:1000].astype(np.float32))
N=len(G)
masks=[(g<thr).astype(np.float32) for g in G]
# for each pair, find integer+subpixel x shift maximizing correlation of masks (y shift allowed +-3)
def best_shift(a,b):
    # shift b to match a: returns dx such that b(x) ~ a(x - dx) i.e. b is a moved by dx
    best=(-1,0,0)
    A=np.fft.rfft2(a); B=np.fft.rfft2(b)
    cc=np.fft.irfft2(np.conj(A)*B, s=a.shape)
    iy,ix=np.unravel_index(np.argmax(cc),cc.shape)
    peak=cc[iy,ix]
    # subpixel x
    l=cc[iy,(ix-1)%cc.shape[1]]; r=cc[iy,(ix+1)%cc.shape[1]]
    sub=0.5*(l-r)/(l-2*peak+r) if (l-2*peak+r)!=0 else 0
    dx=ix+sub; dy=iy
    if dx>cc.shape[1]/2: dx-=cc.shape[1]
    if dy>cc.shape[0]/2: dy-=cc.shape[0]
    norm=peak/np.sqrt((a*a).sum()*(b*b).sum())
    return dx,dy,norm
res=[]
for i in range(N):
    for j in range(i+6,N):
        dx,dy,nc=best_shift(masks[i],masks[j])
        res.append((i,j,dx,dy,nc,dx/(j-i)))
R=np.array(res)
# keep high-similarity pairs (same gait phase) with long baselines
for lagmin in [10,20,30]:
    sel=R[(R[:,1]-R[:,0]>=lagmin)]
    top=sel[sel[:,4]>=np.quantile(sel[:,4],0.9)]
    print(v,'lag>=%d'%lagmin,'n',len(top),'median px/frame %.4f'%np.median(top[:,5]),'mean %.4f'%top[:,5].mean(),'std %.4f'%top[:,5].std(),'nc min %.3f'%top[:,4].min())
# similarity vs lag to find gait period
for lag in range(6,40):
    s=R[(R[:,1]-R[:,0])==lag]
    print(lag,'%.3f'%s[:,4].mean(), '%.3f'%np.median(s[:,5]), end=' | ')
print()
