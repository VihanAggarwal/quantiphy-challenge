import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
orb=cv2.ORB_create(5000); bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
REF=15
kr,dr=orb.detectAndCompute(g[REF],None)
al=[]
for i in range(30):
    k,d=orb.detectAndCompute(g[i],None); m=bf.match(d,dr)
    src=np.float32([k[x.queryIdx].pt for x in m]); dst=np.float32([kr[x.trainIdx].pt for x in m])
    H,_=cv2.findHomography(src,dst,cv2.RANSAC,2.0)
    al.append(cv2.warpPerspective(fr[i],H,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE).astype(np.float32))
bg=np.median(np.stack(al),axis=0)
cv2.imwrite('research/next/audit3/internet_11/remeasure/png/bg47_ref15.png',bg.astype(np.uint8))
res=[]
for i in range(2,26):
    d=np.abs(al[i]-bg).sum(axis=2)
    d=cv2.GaussianBlur(d,(5,5),0)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    j=1+np.argmax(st[1:,4]); x,y,w,h,a=st[j]
    # vertical extent per column -> center row
    ys,xs=np.nonzero(lab==j)
    # top/bottom using columns in the middle third
    cy=(y+y+h)/2
    rows=slice(int(cy-12),int(cy+13))
    prof=d[rows,:].mean(axis=0)
    plat=np.median(prof[x+w//2-40:x+w//2+40])
    half=plat/2
    # left crossing
    xs0=max(x-30,0); seg=prof[xs0:x+w//2]
    k=np.nonzero((seg[:-1]-half)*(seg[1:]-half)<=0)[0]
    L=np.nan;R=np.nan
    if len(k):
        kk=k[0]; L=xs0+kk+(half-seg[kk])/(seg[kk+1]-seg[kk])
    xe=min(x+w+30,1919); seg=prof[x+w//2:xe]
    k=np.nonzero((seg[:-1]-half)*(seg[1:]-half)<=0)[0]
    if len(k):
        kk=k[-1]; R=x+w//2+kk+(half-seg[kk])/(seg[kk+1]-seg[kk])
    # vertical: column profile at center
    xc=(L+R)/2 if np.isfinite(L) and np.isfinite(R) else x+w/2
    cols=slice(int(xc-8),int(xc+9))
    vp=d[:,cols].mean(axis=1)
    platv=np.median(vp[int(cy-40):int(cy+40)]); hv=platv/2
    seg=vp[y-30:int(cy)]; k=np.nonzero((seg[:-1]-hv)*(seg[1:]-hv)<=0)[0]; T=y-30+k[0]+(hv-seg[k[0]])/(seg[k[0]+1]-seg[k[0]]) if len(k) else np.nan
    seg=vp[int(cy):y+h+30]; k=np.nonzero((seg[:-1]-hv)*(seg[1:]-hv)<=0)[0]; B=int(cy)+k[-1]+(hv-seg[k[-1]])/(seg[k[-1]+1]-seg[k[-1]]) if len(k) else np.nan
    res.append((i,L,R,(L+R)/2,R-L,T,B,(T+B)/2,B-T))
    print('%2d L %.1f R %.1f xc %.1f W %.1f  T %.1f B %.1f yc %.1f H %.1f'%res[-1])
np.savetxt('research/next/audit3/internet_11/remeasure/track47b.txt',np.array(res),fmt='%.2f')
