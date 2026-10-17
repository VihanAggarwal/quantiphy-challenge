import cv2, numpy as np
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4')
    out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
def crop(img,x0,x1,y0,y1,s=1):
    c=img[y0:y1,x0:x1]
    if s!=1: c=cv2.resize(c,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
    return c
