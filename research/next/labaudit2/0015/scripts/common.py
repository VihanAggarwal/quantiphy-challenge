import cv2, numpy as np
R='/home/user/quantiphy-challenge/data/QuantiPhy/'
V={'o':'captured_0015','s':'captured_0015s','x':'captured_0015x'}
_cache={}
def load(tag):
    if tag in _cache: return _cache[tag]
    c=cv2.VideoCapture(R+V.get(tag,tag)+'.mp4'); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    _cache[tag]=fr
    return fr
F=711.0; CX=640.0; CY=360.0
# capture index for video frame k: drops before video 12, 36, 60
def cap(k): return k + (k>=12) + (k>=36) + (k>=60)
def ray(u,v):
    d=np.array([(u-CX)/F,(v-CY)/F,1.0]); return d/np.linalg.norm(d)
