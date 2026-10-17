import cv2, numpy as np
W='/home/user/quantiphy-challenge/research/next/audit3/internet_07/'
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0069.mp4'
cap=cv2.VideoCapture(p); G=[]
while True:
    ok,im=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
e=np.loadtxt(W+'edges69.txt'); E={int(r[0]):r for r in e}
b=np.loadtxt(W+'tr69b.txt'); B={int(r[0]):r[3] for r in b}
def sp(a,b,c):
    d=a-2*b+c; return 0 if d==0 else 0.5*(a-c)/d
out={}
for reff in (64,69,74):
    off=B[reff]-B[69]
    x0,x1=int(1040+off),int(1205+off); y0,y1=600,800
    T=G[reff][y0:y1,x0:x1]; w=x1-x0
    for f in range(57,78):
        cx=B[f]-B[69]+1122
        sx0=int(max(0,cx-w/2-40)); sx1=int(min(1920,cx+w/2+40))
        S=G[f][y0-10:y1+10,sx0:sx1]
        if S.shape[1]<w+3: continue
        r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r); x,y=ml
        dx=sp(r[y,x-1],r[y,x],r[y,x+1]) if 0<x<r.shape[1]-1 else 0
        out.setdefault(reff,{})[f]=(sx0+x+dx-x0+B[reff], mv)
fps=30.013
fr=np.arange(57,78)
print('f  '+'  '.join('hh%d'%r for r in out))
for f in fr: print(f,'  '.join('%7.1f(%.2f)'%out[r].get(f,(np.nan,0)) for r in out))
arr=np.array([[f]+[out[r].get(f,(np.nan,0))[0] for r in out] for f in fr])
np.savetxt(W+'hh69.txt',arr,fmt='%.2f')
for j,r in enumerate(out):
    x=arr[:,j+1]
    s=[]
    for lo,hi in ((60,69),(59,72),(60,72),(62,75),(60,75),(63,72)):
        m=(fr>=lo)&(fr<=hi)&np.isfinite(x); t=fr[m]/fps; c=np.polyfit(t,x[m],2); rr=x[m]-np.polyval(c,t)
        s.append('%d-%d a=%.0f r%.2f'%(lo,hi,2*c[0],rr.std()))
    print('hh%d'%r,' | '.join(s))
    print('   frame dx',np.round(np.diff(x),1))
