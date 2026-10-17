import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0024.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(cv2.cvtColor(cv2.resize(f,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2GRAY))
guess={10:(3109,1423),11:(3064,1482),12:(3018,1482),13:(2964,1509),14:(2905,1523),15:(2845,1559)}
cen={}
for k,(gx,gy) in guess.items():
    gx//=2; gy//=2; r=140
    sub=fr[k][gy-r:gy+r,gx-r:gx+r]
    for thr in (60,80):
        m=(sub<thr).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
        n,lab,st,cc=cv2.connectedComponentsWithStats(m)
        d=[(np.hypot(cc[j][0]-r,cc[j][1]-r),j) for j in range(1,n) if st[j,4]>3000]
        if not d: continue
        j=min(d)[1]
        print(k,thr,'coffee c=(%.0f,%.0f) w%d h%d a%d'%((cc[j][0]+gx-r)*2,(cc[j][1]+gy-r)*2,st[j,2]*2,st[j,3]*2,st[j,4]*4))
        if thr==80: cen[k]=((cc[j][0]+gx-r)*2,(cc[j][1]+gy-r)*2)
# template match: patch of coffee+rim
for k in range(10,15):
    cx,cy=[int(v/2) for v in cen[k]]; r=110
    T=fr[k][cy-r:cy+r,cx-r:cx+r]
    S=fr[k+1][cy-r-120:cy+r+120,cx-r-120:cx+r+120]
    res=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED); _,mx,_,loc=cv2.minMaxLoc(res)
    dx=loc[0]-120; dy=loc[1]-120
    print('TM %d->%d d=(%d,%d) full-res step %.1f score %.2f'%(k,k+1,dx*2,dy*2,2*np.hypot(dx,dy),mx))
ks=sorted(cen)
for a,b in zip(ks,ks[1:]):
    print('centroid step %d->%d %.1f'%(a,b,np.hypot(cen[b][0]-cen[a][0],cen[b][1]-cen[a][1])))
