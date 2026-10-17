from load import load
import numpy as np, cv2
fr=[f.astype(np.float32) for f in load()]
def shift1d(a,b,maxs=15):
    # find subpixel shift s such that b(y) ~ a(y - s)
    a=(a-a.mean())/a.std(); b=(b-b.mean())/b.std()
    best=[]
    n=len(a)
    ss=np.arange(-maxs,maxs+1)
    c=[np.mean(a[maxs:n-maxs]*b[maxs+s:n-maxs+s]) for s in ss]
    k=int(np.argmax(c))
    if 0<k<len(c)-1:
        y0,y1,y2=c[k-1],c[k],c[k+1]; d=0.5*(y0-y2)/(y0-2*y1+y2)
    else: d=0
    return ss[k]+d, c[k]
ref=fr[100]
for cols in [(1650,1900),(30,300)]:
    print('cols',cols)
    pA=lambda f: np.diff(f[540:720,cols[0]:cols[1]].mean(1))
    pB=lambda f: np.diff(f[900:1078,cols[0]:cols[1]].mean(1))
    pW=lambda f: np.diff(f[0:200,cols[0]:cols[1]].mean(1))
    for i in range(50,100):
        sA,cA=shift1d(pA(ref),pA(fr[i])); sB,cB=shift1d(pB(ref),pB(fr[i]))
        print(i,'A %+.2f(%.2f) B %+.2f(%.2f)  B-A %+.2f -> s-1=%.4f'%(sA,cA,sB,cB,sB-sA,(sB-sA)/(990-630)))
