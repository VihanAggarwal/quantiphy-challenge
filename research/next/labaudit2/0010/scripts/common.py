import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0010%s.mp4'
F=711.0; CX=640.0; CY=360.0
def frames(r=''):
    c=cv2.VideoCapture(V%r); out=[]
    while True:
        ok,im=c.read()
        if not ok: break
        out.append(im)
    return out
def ray(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
def cap(k, drops=(12,36)):
    return k+sum(k>=d for d in drops)
