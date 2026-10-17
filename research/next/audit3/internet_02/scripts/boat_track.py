# Track the speedboat in internet_0070 (0030 = 0070 frames 44..85). Template match + camera shift from trees.
import cv2, numpy as np
P='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0070.mp4'
c=cv2.VideoCapture(P); G=[]
while True:
    ok,im=c.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
N=len(G)
# camera shift relative to frame 0: phase correlation on tree band y 0..380, chained every frame
win=cv2.createHanningWindow((1920,380),cv2.CV_32F)
cam=np.zeros((N,2))
for i in range(1,N):
    sh,_=cv2.phaseCorrelate(G[i-1][0:380],G[i][0:380],win)
    cam[i]=cam[i-1]+np.array(sh)
# also direct to frame 0 as a check
cam0=np.array([cv2.phaseCorrelate(G[0][0:380],G[i][0:380],win)[0] for i in range(N)])
# template from frame 60: boat hull+bimini, x 640..830, y 600-? (boat ~ y 445..520)
T=G[60][440:525,650:840].copy()
pos=np.full((N,2),np.nan); sc=np.zeros(N)
prev=None
for i in range(10,N):
    # search band
    band=G[i][400:570]
    r=cv2.matchTemplate(band,T,cv2.TM_CCOEFF_NORMED)
    if prev is not None:
        mask=np.full(r.shape,-1.0,np.float32); x0=int(max(0,prev-80)); x1=int(min(r.shape[1],prev+120)); mask[:,x0:x1]=r[:,x0:x1]; r=mask
    _,mx,_,ml=cv2.minMaxLoc(r)
    x,y=ml
    # subpixel parabola
    dx=0;dy=0
    if 0<x<r.shape[1]-1:
        a,b,cc=r[y,x-1],r[y,x],r[y,x+1]; den=a-2*b+cc; dx=0.5*(a-cc)/den if den!=0 else 0
    if 0<y<r.shape[0]-1:
        a,b,cc=r[y-1,x],r[y,x],r[y+1,x]; den=a-2*b+cc; dy=0.5*(a-cc)/den if den!=0 else 0
    pos[i]=(x+dx+650-650, y+dy+400)  # left edge of template in image coords
    sc[i]=mx
    if mx>0.5: prev=x
np.savez('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/i02/boat_track.npz',pos=pos,sc=sc,cam=cam,cam0=cam0)
for i in range(10,N,5):
    print(i, np.round(pos[i],1), round(sc[i],3), np.round(cam[i],1), np.round(cam0[i],1))
