import cv2, numpy as np, sys, json
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_04/'
def read_all(i):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{i:04d}.mp4')
    F=[]
    while True:
        ok,f=c.read()
        if not ok: break
        F.append(f)
    return F
import os
def build_bg(F):
    if os.environ.get('BG')=='last': return F[-1].copy(), -1
    a=F[0].astype(np.int16); b=F[-1].astype(np.int16)
    d=np.abs(a-b).max(2)>25
    col=d.sum(0)
    xs=np.where(col>3)[0]
    # find the gap: largest run of zero columns between xs.min and xs.max
    best=(0,None)
    run=0
    for x in range(xs.min(), xs.max()+1):
        if col[x]<=3:
            run+=1
            if run>best[0]: best=(run,x-run//2)
        else: run=0
    split=best[1] if best[1] is not None else (xs.min()+xs.max())//2
    bg=F[-1].copy(); bg[:,:split]=F[0][:,:split]
    return bg, split
def mask_of(f,bg,thr,ymax=None,sat=None):
    d=np.abs(f.astype(np.int16)-bg.astype(np.int16)).max(2)
    m=(d>thr).astype(np.uint8)
    if sat is not None:
        hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
        m&=(hsv[...,1]>sat).astype(np.uint8)
    if ymax is not None: m[ymax:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<=1: return None
    big=np.argmax(st[1:,4])+1
    keep=np.zeros(n,bool)
    bx,by,bw,bh,ba=st[big]
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a>=max(30,0.002*ba):
            # near the main blob
            if x<bx+bw+80 and x+w>bx-80 and y<by+bh+80 and y+h>by-80: keep[k]=True
    mm=keep[lab]
    return mm
if __name__=='__main__':
    i=int(sys.argv[1]); thr=int(sys.argv[2]); ymax=int(sys.argv[3]) if len(sys.argv)>3 and sys.argv[3]!='-' else None
    sat=int(sys.argv[4]) if len(sys.argv)>4 else None
    F=read_all(i); bg,split=build_bg(F)
    print('split',split)
    rows=[]
    for n,f in enumerate(F):
        m=mask_of(f,bg,thr,ymax,sat)
        if m is None: rows.append([n]+[np.nan]*6); continue
        ys,xs=np.nonzero(m)
        rows.append([n,xs.min(),xs.max(),ys.min(),ys.max(),xs.mean(),ys.mean()])
    rows=np.array(rows,float)
    np.savetxt(W+f'trk_{i}.txt',rows,fmt='%.2f')
    for r in rows[::int(os.environ.get('STEP','4'))]: print(' '.join(f'{v:.1f}' for v in r), ' w=%.0f h=%.0f'%(r[2]-r[1]+1,r[4]-r[3]+1))
