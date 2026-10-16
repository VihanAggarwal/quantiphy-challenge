import cv2, numpy as np
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
O='/home/user/quantiphy-challenge/research/next/labaudit/0062/'
F=711.0; CX=640.0; CY=360.0
def load(s=''):
    c=cv2.VideoCapture(D+'captured_0062%s.mp4'%s)
    fs=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fs.append(f)
    return np.array(fs)
def ray(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
