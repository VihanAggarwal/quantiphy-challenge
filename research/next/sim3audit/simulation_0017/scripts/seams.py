import cv2,numpy as np
med=cv2.imread('frames/median_up.png'); g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY).astype(np.float32)
H,W=g.shape
S=400.0  # px per unit X/Hc
cols=np.linspace(-2.0,2.0,1601)
def rect(y0,y1):
    out=np.full((y1-y0,len(cols)),np.nan,np.float32)
    for r,y in enumerate(range(y0,y1)):
        v=y-540; xs=540+cols*v; ok=(xs>=0)&(xs<W-1)
        x0=np.floor(xs[ok]).astype(int); fx=xs[ok]-x0
        out[r,ok]=g[y,x0]*(1-fx)+g[y,x0+1]*fx
    return out
for (y0,y1) in [(990,1080),(940,1030),(860,960)]:
    R=rect(y0,y1)
    prof=np.nanmean(R,0)
    # seams are dark thin lines: find local minima of profile minus smoothed
    sm=cv2.GaussianBlur(prof.reshape(1,-1).astype(np.float32),(0,0),8).ravel()
    d=prof-sm
    idx=[i for i in range(3,len(d)-3) if d[i]==np.nanmin(d[i-3:i+4]) and d[i]<-4]
    print(y0,y1,[(round(cols[i],4),round(float(d[i]),1)) for i in idx])
