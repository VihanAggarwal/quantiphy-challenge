import cv2, numpy as np
def load(path='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0069.mp4', gray=True):
    c=cv2.VideoCapture(path); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) if gray else f)
    return fr
