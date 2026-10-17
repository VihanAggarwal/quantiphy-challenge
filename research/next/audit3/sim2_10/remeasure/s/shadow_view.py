import cv2, numpy as np
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_10/remeasure/'
V='/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0246.mp4'
c=cv2.VideoCapture(V); F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.int16))
F=np.array(F)
# f0 vs f74 difference: positive where f74 darker than f0
d=F[74]-F[0]
im=np.clip(128+4*d,0,255).astype(np.uint8)
cv2.imwrite(W+'d74m0.png',cv2.resize(im,(960,540),interpolation=cv2.INTER_AREA))
