import cv2,sys,numpy as np
# usage: cdiff.py vid thr amin amax x0 y0 x1 y1 [f0 f1]  colour-diff vs median background
vid=sys.argv[1]; thr=float(sys.argv[2]); amin,amax=float(sys.argv[3]),float(sys.argv[4])
x0,y0,x1,y1=map(int,sys.argv[5:9])
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/internet_{vid}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f[y0:y1,x0:x1])
fr=np.array(fr); bg=np.median(fr,axis=0).astype(np.float32)
f0=int(sys.argv[9]) if len(sys.argv)>9 else 0; f1=int(sys.argv[10]) if len(sys.argv)>10 else len(fr)
for i in range(f0,f1):
    d=np.abs(fr[i].astype(np.float32)-bg).sum(2)
    m=(d>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,l,st,cen=cv2.connectedComponentsWithStats(m)
    out=[]
    idx=sorted(range(1,n),key=lambda k:-st[k,4])
    for k in idx:
        a=st[k,4]
        if amin<=a<=amax:
            out.append(f"({cen[k][0]+x0:.1f},{cen[k][1]+y0:.1f},a{a},w{st[k,2]},h{st[k,3]})")
    print(i,' '.join(out[:8]))
