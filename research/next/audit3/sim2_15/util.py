import cv2, numpy as np
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_15/'
def frames(v):
    c=cv2.VideoCapture(D+f'simulation_{v}.mp4'); out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
def montage(v, idx, scale=0.25, name=None):
    fr=frames(v); ims=[cv2.resize(fr[i],None,fx=scale,fy=scale) for i in idx]
    for i,im in zip(idx,ims): cv2.putText(im,str(i),(5,20),0,0.6,(0,0,255),2)
    rows=[np.hstack(ims[k:k+2]) if len(ims[k:k+2])==2 else np.hstack([ims[k],np.zeros_like(ims[k])]) for k in range(0,len(ims),2)]
    cv2.imwrite(W+'png/'+(name or f'm_{v}.png'), np.vstack(rows))
