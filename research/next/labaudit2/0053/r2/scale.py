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
def mask(f):
    F=f.astype(float); gr=F[...,1]-np.maximum(F[...,0],F[...,2]); return (gr<125).astype(np.uint8)
sift=cv2.SIFT_create()
def feats(i):
    m=mask(FX[i]); 
    yy,xx=np.mgrid[0:720,0:1280]; m[(xx-985.9)**2+(yy-369.6)**2<38**2]=0
    m[:, :400]=0; m[600:]=0
    m=cv2.erode(m,np.ones((5,5),np.uint8))
    g=cv2.cvtColor(FP[i],cv2.COLOR_BGR2GRAY)
    kp,des=sift.detectAndCompute(g,m)
    return kp,des
ref=10
kr,dr=feats(ref)
bf=cv2.BFMatcher()
out={}
for i in range(48):
    k,d=feats(i)
    ms=bf.knnMatch(dr,d,k=2)
    good=[a for a,b in ms if a.distance<0.75*b.distance]
    if len(good)<6: print(i,'few',len(good)); continue
    src=np.float32([kr[g.queryIdx].pt for g in good]); dst=np.float32([k[g.trainIdx].pt for g in good])
    M,inl=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2.0)
    s=np.hypot(M[0,0],M[1,0]); rot=np.degrees(np.arctan2(M[1,0],M[0,0]))
    # also full affine
    M2,inl2=cv2.estimateAffine2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2.0)
    det=np.sqrt(abs(np.linalg.det(M2[:,:2])))
    out[i]=dict(s=float(s),rot=float(rot),n=int(inl.sum()),detscale=float(det))
    print(f"{i:2d} matches {len(good):3d} inl {int(inl.sum()):3d} scale {s:.4f} rot {rot:6.2f}  affine sqrt(det) {det:.4f}  1/s {1/s:.4f}")
json.dump(out,open('scale.json','w'))
