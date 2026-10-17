import cv2, numpy as np
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_10/remeasure/'
V='/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0246.mp4'
c=cv2.VideoCapture(V); F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(f)
F=np.array(F); n=len(F)
bg=np.median(F[::3],axis=0).astype(np.float32)
for i in (0,74):
    d=bg.mean(2)-F[i].astype(np.float32).mean(2)   # darker than bg positive
    im=np.clip(128+3*d,0,255).astype(np.uint8)
    cv2.imwrite(W+'diff%02d.png'%i, cv2.resize(im,(960,540)))
cv2.imwrite(W+'bg_small.png', cv2.resize(bg.astype(np.uint8),(960,540)))
