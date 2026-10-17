import cv2, numpy as np
W='/home/user/quantiphy-challenge/research/next/audit3/internet_07/'
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0064.mp4'); G=[]
while True:
    ok,im=cap.read()
    if not ok: break
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32); G.append(g)
H=[g-cv2.GaussianBlur(g,(0,0),12) for g in G]
reff=100
ball={int(r[0]):(r[1],r[2]) for r in np.loadtxt(W+'ball64.txt')}
def person_x(f):
    # rough: person box from earlier red-mask run: x 30-260 till 118, then moves
    if f<=118: return (0,330)
    c={120:132,126:165,132:225,138:284,144:347,150:437,156:522,162:609,168:698}
    ks=sorted(c); xc=np.interp(f,ks,[c[k] for k in ks]); return (xc-200,xc+200)
PW,PH=200,120
cents=[(x,y) for y in range(40,1080-PH-25,60) for x in range(30,1920-PW-30,80)]
def sp(a,b,c):
    d=a-2*b+c; return 0 if d==0 else 0.5*(a-c)/d
res=[]
for f in range(60,170):
    plo,phi=person_x(f); bx=ball.get(f, ball.get(f-1,(None,None)))
    X=[];D=[]
    for x,y in cents:
        if not (x+PW<plo or x>phi): continue
        if bx[0] is not None and abs(x+PW/2-bx[0])<PW/2+120 and abs(y+PH/2-bx[1])<PH/2+120: continue
        if reff in ball and abs(x+PW/2-ball[reff][0])<PW/2+120 and abs(y+PH/2-ball[reff][1])<PH/2+120: continue
        T=H[reff][y:y+PH,x:x+PW]
        if T.std()<0.8: continue
        m=22; S=H[f][y-m:y+PH+m,x-m:x+PW+m] if y>=m else None
        if S is None or S.shape[0]<PH+2*m or S.shape[1]<PW+2*m: continue
        r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r); xx,yy=ml
        if mv<0.5 or not (0<xx<r.shape[1]-1 and 0<yy<r.shape[0]-1): continue
        if r[yy,xx-1]-2*r[yy,xx]+r[yy,xx+1]>-0.002: continue
        X.append((x+PW/2,y+PH/2)); D.append((xx+sp(r[yy,xx-1],r[yy,xx],r[yy,xx+1])-m, yy+sp(r[yy-1,xx],r[yy,xx],r[yy+1,xx])-m))
    X=np.array(X); D=np.array(D)
    if len(X)<6: print(f,'few',len(X)); continue
    def fit(idx):
        A=[];b=[]
        for (x,y),(dx,dy) in zip(X[idx],D[idx]):
            A.append([1,0,x-960,-(y-540)]); b.append(dx); A.append([0,1,y-540,(x-960)]); b.append(dy)
        return np.linalg.lstsq(np.array(A),np.array(b),rcond=None)[0]
    def pred(c):
        x=X[:,0]-960;y=X[:,1]-540; return np.stack([c[0]+c[2]*x-c[3]*y, c[1]+c[3]*x+c[2]*y],1)
    rng=np.random.default_rng(0); best=None
    for it in range(300):
        idx=rng.choice(len(X),3,replace=False); c=fit(idx); inl=np.linalg.norm(pred(c)-D,axis=1)<0.7
        if best is None or inl.sum()>best[1].sum(): best=(c,inl)
    c=fit(best[1]); inl=np.linalg.norm(pred(c)-D,axis=1)<0.7; c=fit(inl)
    res.append((f,*c,inl.sum(),len(X)))
    if f%4==0 or 80<=f<=146 and f%2==0: print('%d tx=%.2f ty=%.2f k=%.5f th=%.5f inl=%d/%d'%(f,*c,inl.sum(),len(X)))
np.savetxt(W+'cam64.txt',np.array(res),fmt='%.5f')
