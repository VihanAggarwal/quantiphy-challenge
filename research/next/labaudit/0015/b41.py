import cv2, numpy as np
R='/home/user/quantiphy-challenge/data/QuantiPhy/'
c=cv2.VideoCapture(R+'captured_0041x.mp4'); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
print(len(fr))
ims=[]
for i in range(28,46,1):
    f=fr[i]
    th=cv2.resize(f,(320,180)); cv2.putText(th,str(i),(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2); ims.append(th)
while len(ims)%6: ims.append(np.zeros_like(ims[0]))
cv2.imwrite('xref/m41.jpg',np.vstack([np.hstack(ims[i:i+6]) for i in range(0,len(ims),6)]),[cv2.IMWRITE_JPEG_QUALITY,85])
