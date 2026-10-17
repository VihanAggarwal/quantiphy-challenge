import cv2, numpy as np
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
def frames(v, idx=None, gray=False, step=1):
    c=cv2.VideoCapture(D+v+'.mp4'); out={}; i=0
    while True:
        ok,im=c.read()
        if not ok: break
        if (idx is None and i%step==0) or (idx is not None and i in idx):
            out[i]=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY) if gray else im
        i+=1
    return out
def median_bg(v, step=4, scale=1.0):
    fr=frames(v, step=step)
    arr=np.stack([cv2.resize(f,None,fx=scale,fy=scale) if scale!=1 else f for f in fr.values()])
    return np.median(arr,axis=0).astype(np.uint8)
