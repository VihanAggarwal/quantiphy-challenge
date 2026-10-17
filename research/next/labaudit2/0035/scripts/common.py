import cv2, numpy as np, json, os
ROOT='/home/user/quantiphy-challenge'
OUT=ROOT+'/research/next/labaudit2/0035'
F=711.0; CX=640.0; CY=360.0
def frames(v):
    c=cv2.VideoCapture(f'{ROOT}/data/QuantiPhy/captured_0035{v}.mp4'); out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
def ray(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
def cap(k):
    # video frame -> capture frame (25 fps), drops after video 11 and 35
    return k if k<=11 else (k+1 if k<=35 else k+2)
