import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0029%s.mp4'
_cache={}
def frames(r=''):
    if r in _cache: return _cache[r]
    c=cv2.VideoCapture(V%r); out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    _cache[r]=out; return out
def crop(img,cx,cy,hw,scale=1):
    x0=max(0,int(cx-hw)); y0=max(0,int(cy-hw)); c=img[y0:int(cy+hw),x0:int(cx+hw)]
    if scale!=1: c=cv2.resize(c,None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
    return c
