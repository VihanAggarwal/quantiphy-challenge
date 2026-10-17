import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
orb=cv2.ORB_create(6000); bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
REF=15
kr,dr=orb.detectAndCompute(g[REF],None)
al=[]
for i in range(30):
    k,d=orb.detectAndCompute(g[i],None); m=bf.match(d,dr)
    src=np.float32([k[x.queryIdx].pt for x in m]); dst=np.float32([kr[x.trainIdx].pt for x in m])
    H,_=cv2.findHomography(src,dst,cv2.RANSAC,1.5)
    al.append(cv2.warpPerspective(fr[i],H,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0)))
bgs=np.median(np.stack(al[8:]),axis=0).astype(np.uint8)  # frames where left region is clear
lab0=cv2.cvtColor(bgs,cv2.COLOR_BGR2Lab).astype(np.float32)
masks={}
vis=[]
for i in range(0,24):
    L=cv2.cvtColor(al[i],cv2.COLOR_BGR2Lab).astype(np.float32)
    d=np.sqrt(((L-lab0)**2).sum(axis=2)); d=cv2.GaussianBlur(d,(5,5),0)
    m=(d>18).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
    n,ll,st,cc=cv2.connectedComponentsWithStats(m)
    j=1+np.argmax(st[1:,4]); blob=(ll==j).astype(np.uint8)
    cnts,_=cv2.findContours(blob,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    blob=np.zeros_like(blob); cv2.drawContours(blob,cnts,-1,1,-1)
    masks[i]=blob
    x,y,w,h,a=cv2.boundingRect(cnts[0])+(0,)
    M=cv2.moments(blob,True)
    # column extents
    cols=blob.sum(axis=0); xs=np.nonzero(cols)[0]
    print(i,'bbox',x,y,w,h,'cx %.1f cy %.1f'%(M['m10']/M['m00'],M['m01']/M['m00']),'maxcol %d'%cols.max())
    if i in (0,3,9,15):
        v=al[i].copy(); cv2.drawContours(v,cnts,-1,(0,255,0),2)
        vis.append(v[300:750, max(0,x-60):max(0,x-60)+420])
w=min(a.shape[1] for a in vis)
cv2.imwrite('research/next/audit3/internet_11/remeasure/png/masks.png',np.hstack([a[:,:w] for a in vis]))
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/masks47.npy',np.stack([masks[i][300:750] for i in range(24)]).astype(np.uint8))
