import cv2,sys,numpy as np
# usage: blobs.py vid ds amin amax thr [f0 f1]
vid=sys.argv[1]; ds=float(sys.argv[2]); amin,amax=float(sys.argv[3]),float(sys.argv[4]); thr=float(sys.argv[5])
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/internet_{vid}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    if ds!=1: g=cv2.resize(g,None,fx=ds,fy=ds,interpolation=cv2.INTER_AREA)
    fr.append(g)
fr=np.array(fr); bg=np.median(fr,axis=0).astype(np.float32)
f0=int(sys.argv[6]) if len(sys.argv)>6 else 0; f1=int(sys.argv[7]) if len(sys.argv)>7 else len(fr)
for i in range(f0,f1):
    d=np.abs(fr[i].astype(np.float32)-bg)
    m=(d>thr).astype(np.uint8)
    n,l,st,cen=cv2.connectedComponentsWithStats(m)
    out=[]
    for k in range(1,n):
        a=st[k,4]
        if amin<=a<=amax:
            out.append(f"({cen[k][0]/ds:.0f},{cen[k][1]/ds:.0f},a{a})")
    print(i,' '.join(out[:12]))
