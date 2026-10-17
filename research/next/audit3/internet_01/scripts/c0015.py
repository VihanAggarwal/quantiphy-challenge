import cv2, numpy as np, json
V='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0015.mp4'
c=cv2.VideoCapture(V); G=[]
while True:
    ok,im=c.read()
    if not ok: break
    G.append(im)
F=np.stack(G); print(F.shape)
g0=cv2.cvtColor(F[0],cv2.COLOR_BGR2GRAY).astype(np.float32)
# camera motion: phase correlation on off-road regions (rows 0-480 and 660-1080)
win=cv2.createHanningWindow((1920,400),cv2.CV_32F)
sh=[]
for i in range(0,len(F),10):
    g=cv2.cvtColor(F[i],cv2.COLOR_BGR2GRAY).astype(np.float32)
    a=cv2.phaseCorrelate(g0[60:460],g[60:460],win)[0]
    b=cv2.phaseCorrelate(g0[670:1070],g[670:1070],win)[0]
    sh.append((i,round(a[0],2),round(a[1],2),round(b[0],2),round(b[1],2)))
print('shifts top/bottom',sh)
bg=np.median(F[::3],axis=0).astype(np.uint8)
gb=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY).astype(float)
for xc in [200,600,960,1300,1700]:
    prof=gb[480:660,xc-60:xc+60].mean(axis=1)
    # local maxima
    pk=[i for i in range(2,len(prof)-2) if prof[i]==prof[i-2:i+3].max() and prof[i]>np.median(prof)+20]
    cents=[]
    for p in pk:
        w=np.clip(prof[p-3:p+4]-np.median(prof),0,None); cents.append(480+(np.arange(p-3,p+4)*w).sum()/w.sum())
    print('lines at x',xc,np.round(cents,1))
# per-frame vehicle extents in upper lane band
res=[]
for i in range(len(F)):
    d=cv2.absdiff(F[i],bg).max(axis=2)[527:563].astype(float)
    col=(d>35).sum(axis=0)
    on=col>=4
    # segments
    segs=[];s=None
    for x in range(1920):
        if on[x] and s is None: s=x
        if (not on[x]) and s is not None:
            segs.append((s,x-1)); s=None
    if s is not None: segs.append((s,1919))
    # merge gaps <6
    m=[]
    for a,b in segs:
        if m and a-m[-1][1]<6: m[-1]=(m[-1][0],b)
        else: m.append((a,b))
    m=[(a,b) for a,b in m if b-a>=12]
    res.append(m)
json.dump(res,open('/home/user/quantiphy-challenge/research/next/audit3/internet_01/s0015.json','w'))
for i in range(0,len(F),5): print(i,res[i])
