import cv2, numpy as np
def find_peaks(x,distance=1,prominence=0):
    import numpy as np
    c=[i for i in range(1,len(x)-1) if x[i]>x[i-1] and x[i]>=x[i+1] and x[i]>prominence]
    c=sorted(c,key=lambda i:-x[i]); keep=[]
    for i in c:
        if all(abs(i-j)>=distance for j in keep): keep.append(i)
    return np.array(sorted(keep)),None
bg=cv2.imread('research/next/audit3/internet_11/remeasure/png/bg47_ref15.png')
g=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY).astype(np.float32)
for (y0,y1) in [(300,455),(515,640),(650,800)]:
    band=g[y0:y1]
    dxx=cv2.Sobel(band,cv2.CV_32F,2,0,ksize=5)
    prof=np.clip(dxx,0,None).mean(axis=0)
    prof=prof-np.convolve(prof,np.ones(41)/41,'same')
    pk,_=find_peaks(prof,distance=35,prominence=np.percentile(prof,90)*0.5)
    pk=pk[(pk>270)&(pk<1700)]
    d=np.diff(pk)
    # robust pitch: fit seam index assuming gaps ~ multiple of pitch
    p0=np.median(d[(d>40)&(d<65)])
    idx=np.round((pk-pk[0])/p0).astype(int)
    # iterative refine
    for _ in range(3):
        A=np.vstack([idx,np.ones_like(idx),idx**2]).T
        c,*_=np.linalg.lstsq(A,pk,rcond=None)
        pred=A@c
        idx=np.round(np.polyval([0,1,0],idx)).astype(int)
    lin=np.polyfit(idx,pk,1)
    quad=np.polyfit(idx,pk,2)
    res=pk-np.polyval(lin,idx)
    print(y0,y1,'n',len(pk),'median gap %.1f'%p0,'linfit pitch %.2f'%lin[0],'quad',np.round(quad,4),'resid rms %.1f'%res.std(), 'maxidx',idx.max())
    print('  gaps',d.tolist())
