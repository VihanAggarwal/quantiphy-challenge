import cv2, numpy as np
def frames(path='/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0011.mp4'):
    cap=cv2.VideoCapture(path); out=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        out.append(f)
    return out
