import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0068.mp4'
cap=cv2.VideoCapture(p); G=[]
while True:
    ok,im=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
bg=np.median(np.stack([G[i] for i in (85,90,96,99)]),0)
res=[]
for f in range(50,78):
    g=G[f]
    capd=np.clip(bg[600:770]-g[600:770]-25,0,None)  # dark cap
    body=np.clip(g[820:950]-bg[820:950]-25,0,None)  # white body
    # rough x: columns with strong cap darkness
    colc=capd.sum(0); colb=body.sum(0)
    if colc.max()<500: continue
    xs=np.arange(1920)
    # restrict to main blob: threshold columns
    def cent(col,frac=0.15):
        m=col>frac*col.max()
        idx=np.where(m)[0]
        # largest run
        runs=np.split(idx,np.where(np.diff(idx)>5)[0]+1)
        r=max(runs,key=lambda r:col[r].sum())
        lo,hi=r[0],r[-1]
        w=col[lo:hi+1]
        return (xs[lo:hi+1]*w).sum()/w.sum(), lo, hi
    cc,cl,ch=cent(colc); bc,bl,bh=cent(colb) if colb.max()>500 else (np.nan,0,0)
    res.append((f,cc,cl,ch,bc,bl,bh))
    print("%d cap %.1f [%d-%d w%d]  body %.1f [%d-%d w%d]"%(f,cc,cl,ch,ch-cl,bc,bl,bh,bh-bl))
np.savetxt('/home/user/quantiphy-challenge/research/next/audit3/internet_07/tr68.txt',np.array(res),fmt='%.2f')
