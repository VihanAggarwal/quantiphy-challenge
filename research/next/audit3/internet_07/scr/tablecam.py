import cv2, numpy as np, sys
p=sys.argv[1]; reff=int(sys.argv[2]); f0,f1=[int(v) for v in sys.argv[3].split(',')]
objfile=sys.argv[4]; out=sys.argv[5]; ymin=int(sys.argv[6]) if len(sys.argv)>6 else 690
cap=cv2.VideoCapture(p); G=[]
cl=cv2.createCLAHE(4.0,(8,8))
while True:
    ok,im=cap.read()
    if not ok: break
    g_=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32); G.append(g_-cv2.GaussianBlur(g_,(0,0),12))
# object x-range per frame: file with columns f, xlo, xhi
O={int(r[0]):(r[1],r[2]) for r in np.loadtxt(objfile)}
PW,PH=260,140
cents=[(x,y) for y in range(ymin,1080-PH-25,40) for x in range(30,1920-PW-30,60)]
def sp(a,b,c):
    d=a-2*b+c; return 0 if d==0 else 0.5*(a-c)/d
R=G[reff]
res=[]
for f in range(f0,f1+1):
    lo,hi=O.get(f,(-1e9,-1e9))
    X=[];D=[]
    for x,y in cents:
        if hi>-1e8 and not (x+PW<lo or x>hi): continue
        T=R[y:y+PH,x:x+PW]
        if T.std()<1.0: continue
        m=22; S=G[f][y-m:y+PH+m,x-m:x+PW+m]
        r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r); xx,yy=ml
        if mv<0.5 or not (0<xx<r.shape[1]-1 and 0<yy<r.shape[0]-1): continue
        dx=xx+sp(r[yy,xx-1],r[yy,xx],r[yy,xx+1])-m; dy=yy+sp(r[yy-1,xx],r[yy,xx],r[yy+1,xx])-m
        # x-informativeness: curvature of response in x
        cx=r[yy,xx-1]-2*r[yy,xx]+r[yy,xx+1]
        if cx>-0.002: continue
        X.append((x+PW/2,y+PH/2)); D.append((dx,dy))
    X=np.array(X); D=np.array(D)
    if len(X)<6: print(f,'too few',len(X)); continue
    def fit(idx):
        A=[];b=[]
        for (x,y),(dx,dy) in zip(X[idx],D[idx]):
            A.append([1,0,x-960,-(y-540)]); b.append(dx)
            A.append([0,1,y-540,(x-960)]); b.append(dy)
        return np.linalg.lstsq(np.array(A),np.array(b),rcond=None)[0]
    def pred(c):
        x=X[:,0]-960;y=X[:,1]-540
        return np.stack([c[0]+c[2]*x-c[3]*y, c[1]+c[3]*x+c[2]*y],1)
    # x-only zoom fit as well: dx = tx + kx*(x-960) - th*(y-540)
    rng=np.random.default_rng(0); best=None
    for it in range(400):
        idx=rng.choice(len(X),3,replace=False); c=fit(idx)
        e=np.linalg.norm(pred(c)-D,axis=1); inl=e<0.7
        if best is None or inl.sum()>best[1].sum(): best=(c,inl)
    inl=best[1]; c=fit(inl); e=np.linalg.norm(pred(c)-D,axis=1); inl=e<0.7; c=fit(inl)
    Ax=np.c_[np.ones(inl.sum()),X[inl,0]-960,X[inl,1]-540]; cx_=np.linalg.lstsq(Ax,D[inl,0],rcond=None)[0]
    res.append((f,c[0],c[1],c[2],c[3],inl.sum(),len(X),cx_[0],cx_[1],X[inl,0].min(),X[inl,0].max()))
    print('%d tx=%.2f ty=%.2f k=%.5f th=%.5f inl=%d/%d | xonly tx=%.2f kx=%.5f | xr %d-%d'%(f,c[0],c[1],c[2],c[3],inl.sum(),len(X),cx_[0],cx_[1],X[inl,0].min(),X[inl,0].max()))
np.savetxt(out,np.array(res),fmt='%.5f')
