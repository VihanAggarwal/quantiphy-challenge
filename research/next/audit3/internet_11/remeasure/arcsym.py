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
al=[]
for i in range(30):
    k,d=orb.detectAndCompute(g[i],None); m=bf.match(d,dr)
    src=np.float32([k[x.queryIdx].pt for x in m]); dst=np.float32([kr[x.trainIdx].pt for x in m])
    H,_=cv2.findHomography(src,dst,cv2.RANSAC,1.5)
    al.append(cv2.warpPerspective(fr[i],H,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT))
    if i==0: H0=H
bgs=np.median(np.stack(al[8:]),axis=0).astype(np.uint8)
lab0=cv2.cvtColor(bgs,cv2.COLOR_BGR2Lab).astype(np.float32)
valid0=cv2.warpPerspective(np.ones((1080,1920),np.uint8),H0,(1920,1080))
def contour(i,xg,yg):
    L=cv2.cvtColor(al[i],cv2.COLOR_BGR2Lab).astype(np.float32)
    d=np.sqrt(((L-lab0)**2).sum(axis=2)); d=cv2.GaussianBlur(d,(3,3),0)
    bot={};top={}
    for x in range(max(0,int(xg-170)),min(1920,int(xg+170))):
        if i==0 and valid0[yg,x]==0: continue
        col=d[:,x]
        # bottom: search from yg+150 upward for crossing of thr
        seg=col[yg+60:yg+160]
        plat=np.median(col[yg+40:yg+80])
        if plat<35: continue
        thr=0.5*plat
        idx=np.nonzero(seg>thr)[0]
        if len(idx)==0: continue
        kk=idx[-1]
        if kk+1>=len(seg): continue
        bot[x]=yg+60+kk+(seg[kk]-thr)/(seg[kk]-seg[kk+1])
    return bot
def symcenter(cont,xg):
    xs=np.array(sorted(cont)); ys=np.array([cont[x] for x in xs])
    best=None
    for xc in np.arange(xg-40,xg+40,0.25):
        # mirror
        xm=2*xc-xs
        ok=(xm>=xs.min())&(xm<=xs.max())
        if ok.sum()<60: continue
        ym=np.interp(xm[ok],xs,ys)
        # only use the curved flanks: points where y < max(y)-5
        w=(ys[ok]<ys.max()-3)
        if w.sum()<30: continue
        e=np.mean(np.abs(ys[ok][w]-ym[w]))
        if best is None or e<best[0]: best=(e,xc,w.sum())
    return best
t=np.loadtxt('research/next/audit3/internet_11/remeasure/track47d.txt')
pos=dict((int(a),b) for a,b in zip(t[:,0],t[:,1]))
for i in range(0,19):
    xg=pos.get(i,90+77*i) if i>=9 else 75+77*i
    yg=int(585-4.6*i)
    b=contour(i,xg,yg)
    r=symcenter(b,xg)
    print(i,'guess %.1f'%xg,'bottom-arc sym centre %.2f err %.2f n %d'%(r[1],r[0],r[2]) if r else None, 'boundary-method %.1f'%pos.get(i,np.nan))
