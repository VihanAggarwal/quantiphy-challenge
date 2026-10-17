import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0044.mp4'
OUT='/home/user/quantiphy-challenge/research/next/audit3/internet_02/remeasure/'
T=np.loadtxt(OUT+'ball_track_full.txt'); D={int(r[0]):r for r in T}
c=cv2.VideoCapture(V); F={}
k=0
while True:
    ok,im=c.read()
    if not ok: break
    if k in (55,56,66,76,86,95,104,120,180): F[k]=im
    k+=1
bgf=F[180]  # ball gone from that area by f180? check by diff
crops=[]
for f in [55,66,76,86,95]:
    cx,cy=D[f][1],D[f][2]
    g=cv2.cvtColor(F[f],cv2.COLOR_BGR2GRAY).astype(float); gb=cv2.cvtColor(bgf,cv2.COLOR_BGR2GRAY).astype(float)
    # vertical profile: mean over 9 central columns
    xs=slice(int(cx)-4,int(cx)+5)
    prof=g[int(cy)-70:int(cy)+71, xs].mean(axis=1); bprof=gb[int(cy)-70:int(cy)+71, xs].mean(axis=1)
    d=prof-bprof
    pk=d[60:81].max(); half=pk/2
    idx=np.nonzero(d>half)[0]
    top,bot=idx.min(),idx.max()
    # subpixel edges
    def edge(i0,i1):
        a,b=d[i0],d[i1]; return i0+(half-a)/(b-a)
    t=edge(top-1,top); b=edge(bot,bot+1)
    ys=slice(int(cy)-2,int(cy)+3)
    hp=g[ys, int(cx)-80:int(cx)+81].mean(axis=0)-gb[ys, int(cx)-80:int(cx)+81].mean(axis=0)
    hh=hp[70:91].max()/2; ii=np.nonzero(hp>hh)[0]
    print('f%d vertical FWHM-diam %.1f px (pk %.0f)  horizontal %.1f px'%(f,b-t,pk,ii.max()-ii.min()+1))
    cr=F[f][int(cy)-60:int(cy)+60,int(cx)-60:int(cx)+60]; crops.append(cv2.resize(cr,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
cv2.imwrite(OUT+'ball_crops.png',np.hstack(crops))
