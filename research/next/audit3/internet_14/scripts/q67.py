import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0067.mp4')
F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(float))
bg=np.median(np.stack([F[0],F[9],F[10],F[11]]),axis=0)
for f in range(2,8):
    out=[]
    for y in (1150,1200,1250,1450,1500,1550):
        row=F[f][y-5:y+5].mean(0); b=bg[y-5:y+5].mean(0)
        d=np.abs(row-b)
        # string also differs; use threshold
        if y<1300:  # cap: dark
            cov=np.clip((b-row)/max(1,np.percentile(b-row,99.5)),0,1)
        else:
            cov=np.clip((row-b)/max(1,np.percentile(row-b,99.5)),0,1)
        sm=np.convolve(cov,np.ones(9)/9,'same')
        idx=np.where(sm>0.5)[0]
        if len(idx)==0: out.append((y,None)); continue
        # largest run
        runs=np.split(idx,np.where(np.diff(idx)>5)[0]+1)
        r=max(runs,key=len)
        i10=np.where(sm>0.1)[0]; i90=np.where(sm>0.9)[0]
        # left edge 10/90 within neighborhood of run
        L=r[0]; R=r[-1]
        out.append((y,L,R,R-L))
    print(f,out)
