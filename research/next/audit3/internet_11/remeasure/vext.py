import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
orb=cv2.ORB_create(6000); bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
kr,dr=orb.detectAndCompute(g[15],None)
out=[]
for i in list(range(0,19)):
    k,d=orb.detectAndCompute(g[i],None); m=bf.match(d,dr)
    src=np.float32([k[x.queryIdx].pt for x in m]); dst=np.float32([kr[x.trainIdx].pt for x in m])
    H,_=cv2.findHomography(src,dst,cv2.RANSAC,1.5)
    a=cv2.warpPerspective(fr[i],H,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(255,0,255)).astype(np.float32)
    s=a.sum(axis=2); s=cv2.GaussianBlur(s,(1,3),0)
    gr=np.gradient(s,axis=0)
    # predicted center from trajectory to set search windows
    yc_guess=int(585-5*i)  # approx (ref15 coords): frame0 ~585, frame15 ~510
    xs=np.arange(0,1920)
    ext=np.full(1920,np.nan)
    xg=int(90+76.5*i)
    for x in range(max(0,xg-200),min(1920,xg+200)):
        if a[yc_guess,x,0]==255 and a[yc_guess,x,1]==0: continue
        t0=yc_guess-150; t1=yc_guess-70; b0=yc_guess+70; b1=yc_guess+150
        gt=gr[t0:t1,x]; gb=gr[b0:b1,x]
        kt=np.argmin(gt); kb=np.argmax(gb)
        if gt[kt]>-15 or gb[kb]<15: continue
        ext[x]=(b0+kb)-(t0+kt)
    # smooth and find plateau
    e=np.where(np.isnan(ext),0,ext)
    es=np.convolve(e,np.ones(7)/7,'same')
    mx=np.nanmax(es)
    sel=np.nonzero(es>mx-4)[0]
    # keep the contiguous run containing argmax
    km=np.argmax(es); run=[km]
    j=km
    while j-1>=0 and es[j-1]>mx-4: j-=1
    lo=j; j=km
    while j+1<1920 and es[j+1]>mx-4: j+=1
    hi=j
    # weighted centre of plateau region where es > mx-12 (wider)
    j=km
    while j-1>=0 and es[j-1]>mx-12: j-=1
    lo2=j; j=km
    while j+1<1920 and es[j+1]>mx-12: j+=1
    hi2=j
    out.append((i,mx,lo,hi,(lo+hi)/2,lo2,hi2,(lo2+hi2)/2))
    print('%2d maxext %.1f plateau(-4) %d-%d mid %.1f | (-12) %d-%d mid %.1f'%out[-1][1:] if False else '%2d maxext %.1f plateau(-4) %d-%d mid %.1f | (-12) %d-%d mid %.1f'%out[-1])
