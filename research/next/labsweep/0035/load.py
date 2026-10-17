import cv2, numpy as np
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_0035{v}.mp4')
    fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    return fr
def greenmask(f):
    f=f.astype(int); b,g,r=f[...,0],f[...,1],f[...,2]
    return (g>150)&(r<120)&(b<120)
