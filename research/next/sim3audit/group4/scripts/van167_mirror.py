# top-down 0167: column profiles (frame - median bg) across the van at the A-pillar (mirror) and mid-body, several frames
import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0167.mp4')
frs=[]
while True:
    ok,f=cap.read()
    if not ok: break
    frs.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
A=np.stack(frs); bg=np.median(A,axis=0)
def extent(i,x0,w=3,thr_d=-10,thr_b=25):
    p=A[i,540:740,x0:x0+w].mean(axis=1); b=bg[540:740,x0:x0+w].mean(axis=1); dd=p-b
    sig=np.nonzero((dd<thr_d)|(dd>thr_b))[0]
    # keep the contiguous run containing the body centre row (~640)
    c=640-540
    s=np.zeros(len(dd),bool); s[sig]=True
    if not s[c]: return None
    lo=c
    while lo>0 and (s[lo-1] or (lo>1 and s[lo-2])): lo-=1
    hi=c
    while hi<len(s)-1 and (s[hi+1] or (hi<len(s)-2 and s[hi+2])): hi+=1
    return 540+lo,540+hi,hi-lo+1
for i in (24,27,30,33,36):
    xm=840+18*(i-30)
    print('frame',i)
    for dx in (-60,-30,-8,-5,-2,0,2,5,8,20):
        print('   x',xm+dx, extent(i,xm+dx))
