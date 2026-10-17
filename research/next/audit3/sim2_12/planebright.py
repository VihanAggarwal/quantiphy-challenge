import cv2, numpy as np, sys
p=sys.argv[1]
cap=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f.astype(np.float32))
bg=np.median(np.stack(fr[36:]+fr[1:12]),axis=0)
for i in range(14,35):
    g=fr[i].mean(axis=2); gb=bg.mean(axis=2)
    d=g-gb; m=(d>25).astype(np.uint8); m[750:]=0; m[:250]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4])
    mm=lab==k
    col=fr[i][mm]; 
    top=np.percentile(g[mm],90)
    print(i, 'cx',round(cen[k][0]),'cy',round(cen[k][1]),'plane mean BGR',col.mean(axis=0).round(1),'p90',round(top,1),'bg under',gb[mm].mean().round(1))
