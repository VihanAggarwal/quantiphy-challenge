import cv2, numpy as np, sys
p = sys.argv[1]
cap = cv2.VideoCapture(p)
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
med = np.median(np.stack(fr[::2]),axis=0)
for i,f in enumerate(fr):
    d = np.abs(f-med)
    d[:, :] = d
    m = d>25
    # restrict to upper region (plane flies near top of board) y 200..700
    m[750:,:]=False
    ys,xs=np.nonzero(m)
    if len(xs)<30: print(i,'none'); continue
    # biggest connected component
    n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    print(i, 'bbox',x,y,w,h,'area',a,'cen',cen[k].round(1))
