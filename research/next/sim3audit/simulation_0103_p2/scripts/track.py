import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
def frames(clip, idx=None):
    c=cv2.VideoCapture(D+clip+'.mp4'); i=0; out={}
    while True:
        ok,im=c.read()
        if not ok: break
        if idx is None or i in idx: out[i]=im
        i+=1
    return out
def fgmask(im, thr=40):
    g=im.astype(int); return ((255*3-g.sum(2))>thr)
def comp_boxes(m, minarea=15):
    n,l,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    return l, st, cen
