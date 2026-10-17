import cv2, numpy as np
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
    out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
