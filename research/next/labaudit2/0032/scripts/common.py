import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0032%s.mp4'
D='/home/user/quantiphy-challenge/research/next/labaudit2/0032/'
F=711.0; CX=640.0; CY=360.0
K=np.array([[F,0,CX],[0,F,CY],[0,0,1.]]); Ki=np.linalg.inv(K)
def frames(r):
    c=cv2.VideoCapture(V%r); out=[]
    while True:
        ok,im=c.read()
        if not ok: break
        out.append(im)
    return out
def ray(p,f=F,cx=CX,cy=CY):
    r=np.array([(p[0]-cx)/f,(p[1]-cy)/f,1.]); return r/np.linalg.norm(r)
# capture index of video frame k (drops after video 11 and 35)
def cap(k): return k+(k>=12)+(k>=36)
