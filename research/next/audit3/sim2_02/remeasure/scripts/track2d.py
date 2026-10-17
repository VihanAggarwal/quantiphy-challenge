import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
def sub(r,i):
    return (r[i-1]-r[i+1])/(2*(r[i-1]-2*r[i]+r[i+1])) if 0<i<len(r)-1 else 0
def track(F, cx0, cy, v, W, H, iters=4, save=None):
    n=len(F)
    def crop(k,cx):
        M=np.float32([[1,0,-(cx-W/2)],[0,1,-(cy-H/2)]])
        return cv2.warpAffine(F[k],M,(W+40,H),flags=cv2.INTER_LINEAR)  # extra width for search
    cx=np.array([cx0+v*k for k in range(n)],float)
    for it in range(iters):
        mean=np.mean([crop(k,cx[k])[:, :W] for k in range(n)],axis=0)
        T=mean[:, W//6:W-W//6]
        new=[]
        for k in range(n):
            M=np.float32([[1,0,-(cx[k]-W/2-20)],[0,1,-(cy-H/2)]])
            S=cv2.warpAffine(F[k],M,(W+40,H),flags=cv2.INTER_LINEAR)
            r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)[0]
            i=np.argmax(r)
            new.append(cx[k]+(i+sub(r,i)-20-W//6))
        cx=np.array(new)
    mean=np.mean([crop(k,cx[k])[:, :W] for k in range(n)],axis=0)
    if save: cv2.imwrite(save,np.clip(mean,0,255).astype(np.uint8))
    return cx,mean
if __name__=='__main__':
    vid=sys.argv[1]
    F=frames(vid,n=49).astype(np.float32)
    k=np.arange(49)
    for spec in sys.argv[2:]:
        nm,cx0,cy,v,W,H=spec.split(':')
        cx,mean=track(F,float(cx0),float(cy),float(v),int(W),int(H),save=f'{vid}_{nm}_mean.png')
        p=np.polyfit(k,cx,1); r=cx-np.polyval(p,k)
        print(f'{nm}: slope {p[0]:.3f} resid {r.std():.2f} half1 {np.polyfit(k[:25],cx[:25],1)[0]:.3f} half2 {np.polyfit(k[24:],cx[24:],1)[0]:.3f} local16-32 {np.polyfit(k[16:33],cx[16:33],1)[0]:.3f} mean-diff {np.mean(np.diff(cx)):.3f}')
