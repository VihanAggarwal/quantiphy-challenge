import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
def track(vid, y0, y1, x_init, v_init, W, n=49, rows_t=None, cols_t=None, iters=3, save=None):
    F=frames(vid,y0,y1)[:n].astype(np.float32)
    H=F.shape[1]
    def crop(k,cx):
        M=np.float32([[1,0,-(cx-W/2)],[0,1,0]])
        return cv2.warpAffine(F[k],M,(W,H),flags=cv2.INTER_LINEAR)
    cx=np.array([x_init+v_init*k for k in range(n)])
    rt=rows_t or (0,H); ct=cols_t or (W//4, 3*W//4)
    for it in range(iters):
        mean=np.mean([crop(k,cx[k]) for k in range(n)],axis=0)
        T=mean[rt[0]:rt[1],ct[0]:ct[1]]
        new=[]
        for k in range(n):
            big=crop(k,cx[k])
            r=cv2.matchTemplate(big[rt[0]:rt[1]],T,cv2.TM_CCOEFF_NORMED)[0]
            i=np.argmax(r)
            d=(r[i-1]-r[i+1])/(2*(r[i-1]-2*r[i]+r[i+1])) if 0<i<len(r)-1 else 0
            new.append(cx[k]+(i+d-ct[0]))
        cx=np.array(new)
    mean=np.mean([crop(k,cx[k]) for k in range(n)],axis=0)
    if save: cv2.imwrite(save, np.clip(mean,0,255).astype(np.uint8))
    return cx, mean
