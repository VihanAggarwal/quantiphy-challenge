import cv2, numpy as np
W='/home/user/quantiphy-challenge/research/next/audit3/internet_07/'
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0069.mp4'
cap=cv2.VideoCapture(p); G=[]
while True:
    ok,im=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
e=np.loadtxt(W+'edges69.txt'); E={int(r[0]):r for r in e}
fps=30.013
# camera-aligned background: warp bg (median of 96..108) by the per-frame similarity from table fit
cam=np.loadtxt(W+'cam69t.txt'); C={int(r[0]):r for r in cam}
bgr=np.median(np.stack([G[i] for i in (96,100,104,108)]),0)
def warp_bg(f):
    if f not in C or f==73: return bgr
    _,tx,ty,k,th=C[f][:5]
    s=1+k
    A=np.array([[s,-th,0],[th,s,0]],np.float32)
    # x' = s*(x-960) - th*(y-540) + 960 + tx
    A[0,2]=960+tx-s*960+th*540; A[1,2]=540+ty-th*960-s*540
    return cv2.warpAffine(bgr,A,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
# lower-handle template from frame 69
T=G[69][700:830,1150:1215].copy()
def sp(a,b,c):
    d=a-2*b+c; return 0 if d==0 else 0.5*(a-c)/d
out=[]
for f in range(58,79):
    r=E[f]; L,R=r[1],r[2]
    bgw=warp_bg(f)
    res=[f]
    for (y0,y1) in ((590,650),(680,760)):
        if not np.isfinite(L) or L<45: res+= [np.nan]; continue
        x0=int(L-40); x1=int(R+12)
        D=(bgw[y0:y1,x0:x1]-G[f][y0:y1,x0:x1])  # body darker than bg -> positive
        w=D.sum(0)
        xs=np.arange(x0,x1)
        res.append((xs*w).sum()/w.sum())
    # lower handle template
    cx=r[2]+175
    sx0=int(max(0,cx-130)); sx1=int(min(1920,cx+130))
    S=G[f][680:850,sx0:sx1]
    if S.shape[1]>T.shape[1]+3:
        rr=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(rr); x,y=ml
        dx=sp(rr[y,x-1],rr[y,x],rr[y,x+1]) if 0<x<rr.shape[1]-1 else 0
        res+=[sx0+x+dx+32.5, mv]
    else: res+=[np.nan,0]
    out.append(res)
    print(' '.join('%.2f'%v for v in res))
out=np.array(out); np.savetxt(W+'mom69.txt',out,fmt='%.3f')
f=out[:,0]
for j,n in ((1,'momUpper'),(2,'momLower'),(3,'lowHandleTM')):
    x=out[:,j]; s=[]
    for lo,hi in ((61,72),(61,75),(62,75),(60,72),(63,72),(64,76)):
        m=(f>=lo)&(f<=hi)&np.isfinite(x)
        if m.sum()<5: continue
        t=f[m]/fps; c=np.polyfit(t,x[m],2); rr=x[m]-np.polyval(c,t)
        s.append('%d-%d a=%.0f r%.2f v2.0=%.0f'%(lo,hi,2*c[0],rr.std(),np.polyval(np.polyder(c),2.0)))
    print(n,' | '.join(s))
