import cv2, numpy as np, sys
c=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]
cap=cv2.VideoCapture(f'data/QuantiPhy/simulation_{c}.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
N=len(fr)
bg=np.median(np.stack(fr[::2]).astype(np.float32),axis=0)
out=[]
for f in frames:
    d=np.abs(fr[f].astype(np.float32)-bg).max(axis=2)
    d=np.clip(d*4,0,255).astype(np.uint8)
    d=cv2.resize(d,(960,540)); cv2.putText(d,str(f),(10,30),0,1,255,2)
    out.append(d)
cv2.imwrite(f'research/next/audit3/sim2_13/img/diff_{c}.png',np.vstack([np.hstack(out[:2]),np.hstack(out[2:4])]))
