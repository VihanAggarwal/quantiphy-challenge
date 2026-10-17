import cv2, numpy as np
W='/home/user/quantiphy-challenge/research/next/audit3/internet_07/'
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0064.mp4'); G=[]
while True:
    ok,im=cap.read()
    if not ok: break
    G.append(im.astype(np.float32))
bgR=np.median(np.stack([G[i] for i in range(0,60,6)]),0)   # valid for x>340
bgL=np.median(np.stack([G[i] for i in (163,166,169)]),0)   # valid for x<520
bg=bgR.copy(); bg[:,:430]=bgL[:,:430]
cam={int(r[0]):r for r in np.loadtxt(W+'cam64.txt')}
out=[]
for f in range(112,170):
    D=np.abs(G[f]-bg).max(2)
    m=(D>35).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    # restrict to person: largest component touching rows 450-1000 and x<1000
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None
    for i in range(1,n):
        x,y,w,h,a=st[i]
        if h>300 and x<1000 and (best is None or a>st[best][4]): best=i
    if best is None: continue
    pm=(lab==best)
    ys,xs=np.where(pm)
    top=ys.min(); bot=ys.max()
    band=pm[560:760]   # torso/hip rows
    cx_t=np.where(band)[1].mean() if band.any() else np.nan
    headb=pm[420:520]; cx_h=np.where(headb)[1].mean() if headb.any() else np.nan
    out.append((f,cx_t,cx_h,xs.mean(),top,bot))
out=np.array(out); np.savetxt(W+'person64.txt',out,fmt='%.2f')
for r in out:
    if r[0]%3==0: print('%d torso %.1f head %.1f all %.1f top %d bot %d'%tuple(r))
