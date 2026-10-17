import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
orb=cv2.ORB_create(5000); bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
kr,dr=orb.detectAndCompute(g[29],None)
al=[]; As=[]
for i in range(30):
    k,d=orb.detectAndCompute(g[i],None); m=bf.match(d,dr)
    src=np.float32([k[x.queryIdx].pt for x in m]); dst=np.float32([kr[x.trainIdx].pt for x in m])
    A,_=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2.0)
    As.append(A)
    al.append(cv2.warpAffine(fr[i],A,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE).astype(np.float32))
bg=np.median(np.stack(al[::1]),axis=0)
res=[]
for i in range(30):
    d=np.abs(al[i]-bg).sum(axis=2)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); continue
    j=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[j]
    ys,xs=np.nonzero(lab==j)
    # vertical extent per column near the center
    cols=np.arange(x,x+w)
    ext=[]
    for cc in cols:
        yy=ys[xs==cc]
        if len(yy): ext.append((cc,yy.min(),yy.max()))
    ext=np.array(ext)
    vh=ext[:,2]-ext[:,1]+1
    print(i,'bbox x%d y%d w%d h%d area%d cen %.1f %.1f maxVext %d p90 %d'%(x,y,w,h,a,cen[j][0],cen[j][1],vh.max(),np.percentile(vh,90)))
    res.append((i,x,y,w,h,cen[j][0],cen[j][1]))
np.savetxt('research/next/audit3/internet_11/remeasure/track47.txt',np.array(res),fmt='%.2f')
cv2.imwrite('research/next/audit3/internet_11/remeasure/png/bg47.jpg',bg.astype(np.uint8)[::2,::2])
