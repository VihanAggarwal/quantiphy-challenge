import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0020.mp4'
cap=cv2.VideoCapture(p); F=[]
while True:
    ok,im=cap.read()
    if not ok: break
    F.append(im[900:2000,2100:3000].copy())
a=F[0].astype(np.float32); b=F[18].astype(np.float32)
d=np.abs(a-b).sum(2); d=np.clip(d*2,0,255).astype(np.uint8)
d=cv2.cvtColor(d,cv2.COLOR_GRAY2BGR)
s=0.5; d=cv2.resize(d,None,fx=s,fy=s)
for gy in range(950,2000,50):
    Y=int((gy-900)*s); cv2.line(d,(0,Y),(d.shape[1],Y),(0,200,255) if gy%100==0 else (0,90,120),1)
    if gy%100==0: cv2.putText(d,str(gy),(2,Y-2),0,0.4,(0,0,255),1)
for gx in range(2150,3000,50):
    X=int((gx-2100)*s); cv2.line(d,(X,0),(X,d.shape[0]),(0,200,255) if gx%100==0 else (0,90,120),1)
    if gx%100==0: cv2.putText(d,str(gx),(X+2,12),0,0.4,(0,0,255),1)
cv2.imwrite('bdiff.png',d)
