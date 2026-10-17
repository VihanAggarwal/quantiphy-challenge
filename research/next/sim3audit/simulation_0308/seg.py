import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0304.mp4')
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f)
f=fr[24].astype(np.float32)
# background model: fit quadratic poly per channel on border pixels / pixels far from whale
H,W=f.shape[:2]
yy,xx=np.mgrid[0:H:8,0:W:8]
s=f[::8,::8]
# rough mask: brightness
g=s.mean(2)
print(np.percentile(g,[1,5,25,50,75,95,99]))
print(s[0,0],s[-1,-1],s[90,160])
