import cv2, numpy as np
R='/home/user/quantiphy-challenge/data/QuantiPhy/'
c=cv2.VideoCapture(R+'captured_0041x.mp4'); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
for i in range(30,41):
    f=fr[i].astype(int)
    green=(f[...,1]>200)&(f[...,0]<80)&(f[...,2]<80)
    fg=~green; fg[650:,1000:]=False
    n,lab,st,cen=cv2.connectedComponentsWithStats(fg.astype(np.uint8))
    out=[]
    for k in range(1,n):
        if st[k][4]>300: out.append((tuple(int(x) for x in st[k]),tuple(round(float(x),1) for x in cen[k])))
    print(i,out)
