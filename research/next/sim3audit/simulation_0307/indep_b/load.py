import cv2, numpy as np
def frames(c):
    v=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{c}.mp4')
    fr=[]
    while True:
        ok,f=v.read()
        if not ok: break
        fr.append(f)
    return fr
def mask0303(f):
    # dark plane vs blue sky
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32)
    b=f[:,:,0].astype(np.float32)
    m=(b<150)
    m[:80]=False; m[-80:]=False
    m=m.astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    if n<=1: return m
    k=1+np.argmax(st[1:,4])
    return (lab==k).astype(np.uint8)
