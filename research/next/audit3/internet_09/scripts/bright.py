import cv2,sys,numpy as np
# usage: bright.py vid sign thr amin amax x0 y0 x1 y1 [f0 f1]  (sign +1 brighter than median bg, -1 darker)
vid=sys.argv[1]; sg=float(sys.argv[2]); thr=float(sys.argv[3]); amin,amax=float(sys.argv[4]),float(sys.argv[5])
x0,y0,x1,y1=map(int,sys.argv[6:10])
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/internet_{vid}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(cv2.cvtColor(f[y0:y1,x0:x1],cv2.COLOR_BGR2GRAY))
fr=np.array(fr); bg=np.median(fr,axis=0).astype(np.float32)
f0=int(sys.argv[10]) if len(sys.argv)>10 else 0; f1=int(sys.argv[11]) if len(sys.argv)>11 else len(fr)
for i in range(f0,f1):
    d=sg*(fr[i].astype(np.float32)-bg)
    m=(d>thr).astype(np.uint8)
    n,l,st,cen=cv2.connectedComponentsWithStats(m)
    out=[]
    for k in range(1,n):
        a=st[k,4]
        if amin<=a<=amax:
            out.append(f"({cen[k][0]+x0:.1f},{cen[k][1]+y0:.1f},a{a},w{st[k,2]},h{st[k,3]})")
    print(i,' '.join(out[:8]))
