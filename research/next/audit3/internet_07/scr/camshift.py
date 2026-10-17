import cv2, sys, numpy as np
p=sys.argv[1]; y0,y1,x0,x1=[int(v) for v in sys.argv[2].split(',')]
cap=cv2.VideoCapture(p); ref=None; f=0; out=[]
while True:
    ok,im=cap.read()
    if not ok: break
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)[y0:y1,x0:x1]
    if ref is None: ref=g
    (dx,dy),r=cv2.phaseCorrelate(ref,g)
    out.append((f,dx,dy,r)); f+=1
for o in out[::5]: print("%d %.2f %.2f %.2f"%o)
