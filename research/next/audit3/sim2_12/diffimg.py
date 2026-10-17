import cv2, numpy as np, sys
p,out,i = sys.argv[1],sys.argv[2],int(sys.argv[3])
gain=float(sys.argv[4]) if len(sys.argv)>4 else 20
cap = cv2.VideoCapture(p)
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
bg = np.median(np.stack(fr[36:]+fr[1:12]),axis=0)
d = cv2.GaussianBlur(fr[i]-bg,(9,9),0)
img = np.clip(128+gain*d,0,255).astype(np.uint8)
img = cv2.resize(img,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
cv2.imwrite(out,img)
