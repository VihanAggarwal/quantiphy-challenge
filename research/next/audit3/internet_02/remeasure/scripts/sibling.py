import cv2, numpy as np
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
def load(v):
    c=cv2.VideoCapture(D+v+'.mp4'); F=[]
    while True:
        ok,im=c.read()
        if not ok: break
        F.append(cv2.resize(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),None,fx=0.25,fy=0.25,interpolation=cv2.INTER_AREA).astype(np.float32))
    return F
A=load('internet_0030'); B=load('internet_0070')
for fa in [0,20,41]:
    errs=[np.mean(np.abs(A[fa]-b)) for b in B]
    k=int(np.argmin(errs)); print('0030 f%d best match 0070 f%d MAD %.2f (next best %.2f)'%(fa,k,errs[k],sorted(errs)[1]))
