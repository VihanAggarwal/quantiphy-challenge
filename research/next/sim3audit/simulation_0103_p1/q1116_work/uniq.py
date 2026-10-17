import cv2, numpy as np
def load(name, seg=False, gray=True):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{name}{"_segmented" if seg else ""}.mp4')
    fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) if gray else f)
    return fr
def dup_mask(name):
    fr=load(name)
    d=[np.abs(fr[i+1].astype(float)-fr[i]).mean() for i in range(len(fr)-1)]
    d=np.array(d); med=np.median(d)
    keep=[0]+[i+1 for i in range(len(d)) if d[i]>=0.3*med]
    return keep
