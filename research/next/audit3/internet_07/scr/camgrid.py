import cv2, sys, numpy as np
p=sys.argv[1]; reff=int(sys.argv[2]); f0,f1=[int(v) for v in sys.argv[3].split(',')]; out=sys.argv[4]
bgfr=[int(v) for v in sys.argv[5].split(',')]
cap=cv2.VideoCapture(p); G=[]
clahe=cv2.createCLAHE(3.0,(8,8))
while True:
    ok,im=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY))
bg=np.median(np.stack([G[i] for i in bgfr]),0).astype(np.uint8)
def hp(g):
    g=clahe.apply(g).astype(np.float32); return g-cv2.GaussianBlur(g,(0,0),6)
R=hp(G[reff]); P=96; win=cv2.createHanningWindow((P,P),cv2.CV_32F)
cent=[(x,y) for y in range(0,1080-P+1,48) for x in range(0,1920-P+1,48)]
res=[]
for f in range(f0,f1+1):
    g=G[f]; H=hp(g)
    d=cv2.absdiff(g,bg); m=(d>25).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    m=cv2.dilate(m,np.ones((41,41),np.uint8))
    X=[];D=[]
    for x,y in cent:
        if m[y:y+P,x:x+P].any(): continue
        (dx,dy),r=cv2.phaseCorrelate(R[y:y+P,x:x+P],H[y:y+P,x:x+P],win)
        if r<0.3 or abs(dx)>30 or abs(dy)>30: continue
        X.append((x+P/2,y+P/2)); D.append((dx,dy))
    X=np.array(X); D=np.array(D)
    # RANSAC similarity: dx=tx+k*x-th*y ; dy=ty+th*x+k*y
    def fit(idx):
        A=[];b=[]
        for (x,y),(dx,dy) in zip(X[idx],D[idx]):
            A.append([1,0,x-960,-(y-540)]); b.append(dx)
            A.append([0,1,y-540,(x-960)]); b.append(dy)
        return np.linalg.lstsq(np.array(A),np.array(b),rcond=None)[0]
    def pred(c):
        x=X[:,0]-960;y=X[:,1]-540
        return np.stack([c[0]+c[2]*x-c[3]*y, c[1]+c[3]*x+c[2]*y],1)
    rng=np.random.default_rng(0); best=None
    for it in range(300):
        idx=rng.choice(len(X),3,replace=False); c=fit(idx)
        e=np.linalg.norm(pred(c)-D,axis=1); inl=e<0.8
        if best is None or inl.sum()>best[1].sum(): best=(c,inl)
    c=fit(best[1]); e=np.linalg.norm(pred(c)-D,axis=1); inl=e<0.8; c=fit(inl)
    res.append([f,c[0],c[1],c[2],c[3],inl.sum(),len(X)])
    # x-spread of inliers
    xs=X[inl,0]
    print(f,'tx=%.2f ty=%.2f k=%.5f th=%.5f inl=%d/%d xrange %d-%d'%(c[0],c[1],c[2],c[3],inl.sum(),len(X),xs.min(),xs.max()))
np.savetxt(out,np.array(res),fmt='%.6f')
