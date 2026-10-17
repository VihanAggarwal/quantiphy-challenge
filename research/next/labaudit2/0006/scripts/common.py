import cv2, numpy as np
R='/home/user/quantiphy-challenge/data/QuantiPhy/'
D='/home/user/quantiphy-challenge/research/next/labaudit2/0006/'
V={'o':'captured_0006','s':'captured_0006s'}
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
def ray(u,v):
    d=np.array([(u-CX)/F,(v-CY)/F,1.0]); return d/np.linalg.norm(d)
def P(u,v,R): return R*ray(u,v)
def ymask(img, hlo=15, hhi=40, smin=90, vmin=90):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, (hlo, smin, vmin), (hhi, 255, 255))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n <= 1: return None
    k = 1 + np.argmax(st[1:, 4])
    return (lab == k), st[k], cen[k]
