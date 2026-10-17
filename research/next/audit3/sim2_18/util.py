import cv2, numpy as np
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_18/'
def frames(v, idx=None):
    c=cv2.VideoCapture(D+v+'.mp4'); out=[]; i=0
    while True:
        ok,f=c.read()
        if not ok: break
        if idx is None or i in idx: out.append((i,f))
        i+=1
    return out
def save(name, img, scale=1.0):
    if scale!=1.0: img=cv2.resize(img,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    cv2.imwrite(W+name, img)
