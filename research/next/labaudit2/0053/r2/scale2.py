import cv2,numpy as np,json
T=json.load(open('bintrack.json'))
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    return fr
FX=frames('captured_0053x'); FP=frames('captured_0053')
def binmask(i):
    F=FX[i].astype(float); gr=F[...,1]-np.maximum(F[...,0],F[...,2]); m=(gr<125).astype(np.uint8)
    yy,xx=np.mgrid[0:720,0:1280]; m[(xx-985.9)**2+(yy-369.6)**2<38**2]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    t=T[i]; k=lab[int(t['cy']),int(t['cx'])]
    if k==0:
        k=1+np.argmax(st[1:,4])
    return (lab==k).astype(np.uint8)
sift=cv2.SIFT_create(contrastThreshold=0.02)
cache={}
def feats(i):
    if i in cache: return cache[i]
    m=cv2.erode(binmask(i),np.ones((5,5),np.uint8))
    g=cv2.cvtColor(FP[i],cv2.COLOR_BGR2GRAY)
    cache[i]=sift.detectAndCompute(g,m); return cache[i]
bf=cv2.BFMatcher()
def match(a,b):
    ka,da=feats(a); kb,db=feats(b)
    ms=bf.knnMatch(da,db,k=2)
    good=[x for x,y in ms if x.distance<0.8*y.distance]
    if len(good)<5: return None
    src=np.float32([ka[g.queryIdx].pt for g in good]); dst=np.float32([kb[g.trainIdx].pt for g in good])
    M,inl=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2.5,maxIters=5000)
    if M is None: return None
    return np.hypot(M[0,0],M[1,0]), int(inl.sum()), len(good)
res={}
for ref in [10,22,34]:
    for i in range(48):
        r=match(ref,i)
        if r: res[(ref,i)]=r
for ref in [10,22,34]:
    print('ref',ref)
    print(' '.join(f"{i}:{res[(ref,i)][0]:.3f}/{res[(ref,i)][1]}" for i in range(48) if (ref,i) in res))
# direct 10->34 and chain
for a,b in [(10,34),(10,22),(22,34),(10,30),(30,34),(8,34),(12,34),(10,36)]:
    print(a,b,match(a,b))
