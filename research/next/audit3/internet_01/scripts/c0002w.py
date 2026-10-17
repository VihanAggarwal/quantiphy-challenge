import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0002.mp4'
c=cv2.VideoCapture(V); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im[950:1450])
F=np.stack(fr); bg=np.median(F,axis=0).astype(np.float32)
cen={8:1363.9,12:1784.9,15:2101.7,20:2630.9,24:3062.0}
for i,cx in cen.items():
    # red-part centroid ~ cab; take columns cx-120..cx+60 (cab roof + hood region, excludes mirrors? mirrors near windshield)
    for off in [-150,-100,-60,60,120]:
        x=int(cx+off)
        col=F[i][:,x-3:x+4].astype(np.float32).mean(axis=1)
        b=bg[:,x-3:x+4].mean(axis=1)
        d=np.abs(col-b).max(axis=1)
        idx=np.where(d>35)[0]
        if len(idx)==0: continue
        # largest contiguous run
        runs=np.split(idx,np.where(np.diff(idx)>3)[0]+1)
        r=max(runs,key=len)
        print(i,off,'y',r[0]+950,r[-1]+950,'w',r[-1]-r[0]+1)
