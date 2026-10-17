# x-extent of the phoenix per frame with a low threshold; contiguous run from the body outward
import cv2, numpy as np, sys, os
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_04/scripts')
from track import read_all, build_bg
i=int(sys.argv[1]); y0=int(sys.argv[2]); y1=int(sys.argv[3]); thr=float(sys.argv[4]); gap=int(sys.argv[5])
F=read_all(i); bg,_=build_bg(F)
out=[]
for n,f in enumerate(F):
    d=np.abs(f.astype(np.int16)-bg.astype(np.int16)).max(2).astype(np.float32)
    d=cv2.GaussianBlur(d,(3,3),0)
    prof=d[y0:y1].max(0)
    on=prof>=thr
    # body centre: column with largest strong-diff count
    strong=(d[y0:y1]>40).sum(0)
    c=int(np.argmax(np.convolve(strong,np.ones(51),'same')))
    # walk right
    x=c; miss=0; xr=c
    while x<2559:
        x+=1
        if on[x]: xr=x; miss=0
        else:
            miss+=1
            if miss>gap: break
    x=c; miss=0; xl=c
    while x>0:
        x-=1
        if on[x]: xl=x; miss=0
        else:
            miss+=1
            if miss>gap: break
    out.append((n,xl,xr,xr-xl+1))
out=np.array(out)
np.savetxt(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_04/xext_{i}_t{int(thr)}.txt',out,fmt='%d')
w=out[:,3]
print(f'clip {i} thr{thr} f0: x[{out[0,1]},{out[0,2]}] w={out[0,3]}  frames0-24 w: min {w[:25].min()} med {np.median(w[:25]):.0f} max {w[:25].max()}; all(0-60 in-frame) med {np.median(w[(out[:,1]>2)&(out[:,2]<2557)]):.0f}')
print(' '.join(f'{a}:{b}' for a,b in zip(out[:30,0],out[:30,3])))
