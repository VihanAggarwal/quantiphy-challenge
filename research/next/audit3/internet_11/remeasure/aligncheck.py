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
def edges(prof,thr):
    xs=[]
    for i in range(len(prof)-1):
        if (prof[i]-thr)*(prof[i+1]-thr)<0: xs.append(i+(thr-prof[i])/(prof[i+1]-prof[i]))
    return xs
for i in range(6,22):
    k,d=orb.detectAndCompute(g[i],None); m=bf.match(d,dr)
    src=np.float32([k[x.queryIdx].pt for x in m]); dst=np.float32([kr[x.trainIdx].pt for x in m])
    H,_=cv2.findHomography(src,dst,cv2.RANSAC,1.5)
    a=cv2.warpPerspective(fr[i],H,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    raw=fr[i].astype(np.float32)
    out=[]
    for img in (a,raw):
        for y in (700,900):
            G=img[y-3:y+4,:,1].mean(axis=0); Bc=img[y-3:y+4,:,0].mean(axis=0); Rc=img[y-3:y+4,:,2].mean(axis=0)
            r=[]
            for (lo,hi) in [(150,330),(1650,1850)]:
                seg=G[lo:hi]; thr=(np.percentile(seg,3)+np.median(seg))/2; xs=edges(-seg,-thr); r.append(lo+(xs[0]+xs[-1])/2)
            w=(Bc-Rc)[1100:1300]; thr=(np.median(w)+np.percentile(w,97))/2; xs=edges(w,thr); r.insert(1,1100+(xs[0]+xs[-1])/2)
            out+=r
    print(i,'aligned y700 %.1f %.1f %.1f | y900 %.1f %.1f %.1f || raw y700 %.1f %.1f %.1f | y900 %.1f %.1f %.1f'%tuple(out))
