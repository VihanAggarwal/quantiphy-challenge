import cv2, numpy as np, sys
V='/home/user/quantiphy-challenge/data/QuantiPhy/simulation_%s.mp4'
def frames(vid):
    c=cv2.VideoCapture(V%vid); out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
def save(img,path,scale=1.0):
    if scale!=1.0: img=cv2.resize(img,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    cv2.imwrite(path,img)
