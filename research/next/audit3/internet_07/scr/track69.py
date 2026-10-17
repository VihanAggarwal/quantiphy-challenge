import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0069.mp4'
cap=cv2.VideoCapture(p); G=[]; C=[]
while True:
    ok,im=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
bg=np.median(np.stack([G[i] for i in (96,100,104,108)]),0)
# template: handle + knot from frame 69
tx0,ty0,tx1,ty1=1110,540,1250,850
T=G[69][ty0:ty1,tx0:tx1]
def sp(a,b,c):
    d=a-2*b+c; return 0 if d==0 else 0.5*(a-c)/d
rows=[]
for f in range(56,84):
    g=G[f]
    band=g[ty0-30:ty1+30]
    r=cv2.matchTemplate(band,T,cv2.TM_CCOEFF_NORMED)
    _,mv,_,ml=cv2.minMaxLoc(r); x,y=ml
    dx=sp(r[y,x-1],r[y,x],r[y,x+1]) if 0<x<r.shape[1]-1 else 0
    hx=x+dx+(tx1-tx0)/2  # handle template centre x
    hy=y+ty0-30-ty0
    # body edges from bg diff, rows 700-1000 (below handle bottom? handle bottom ~ 820)
    D=np.abs(g[880:1040]-bg[880:1040])
    col=(D>20).mean(0)
    idx=np.where(col>0.5)[0]
    if len(idx):
        runs=np.split(idx,np.where(np.diff(idx)>8)[0]+1); rr=max(runs,key=len); L,R=rr[0],rr[-1]
    else: L=R=np.nan
    rows.append((f,hx,mv,hy,L,R))
    print('%d handle %.1f (%.2f, dy %.1f)  body L %s R %s mid %.1f w %s'%(f,hx,mv,hy,L,R,(L+R)/2,R-L))
np.savetxt('/home/user/quantiphy-challenge/research/next/audit3/internet_07/tr69.txt',np.array(rows,float),fmt='%.2f')
