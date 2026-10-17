import cv2, numpy as np, sys
p = sys.argv[1]
cap = cv2.VideoCapture(p)
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
bg = np.median(np.stack(fr[36:]+fr[1:12]),axis=0)
for i in range(13,36):
    d = cv2.GaussianBlur(fr[i]-bg,(5,5),0)
    neg = (d< -6).astype(np.uint8); pos=(d>15).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(neg)
    big=[(tuple(st[k][:4]),st[k][4]) for k in range(1,n) if st[k][4]>40]
    n2,lab2,st2,cen2=cv2.connectedComponentsWithStats(pos)
    bigp=[(tuple(st2[k][:4]),st2[k][4]) for k in range(1,n2) if st2[k][4]>40]
    print(i,'NEG',big[:6],'POS',bigp[:4])
