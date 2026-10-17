import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0044.mp4'
OUT='/home/user/quantiphy-challenge/research/next/audit3/internet_02/remeasure/'
c=cv2.VideoCapture(V); frames=[]
while True:
    ok,im=c.read()
    if not ok: break
    frames.append(im)
N=len(frames)
bg=np.median(np.stack(frames[::5]),axis=0).astype(np.uint8)
# camera shift per frame (phase correlation vs frame 75 on wall/monitor/lamp region, no ball there)
gref=cv2.cvtColor(frames[75],cv2.COLOR_BGR2GRAY).astype(np.float32)[60:420,1400:1900]
cam={}
for i in range(40,150):
    gi=cv2.cvtColor(frames[i],cv2.COLOR_BGR2GRAY).astype(np.float32)[60:420,1400:1900]
    (dx,dy),r=cv2.phaseCorrelate(gref,gi); cam[i]=(dx,dy,r)
rows=[]
prev=np.array([1665.,480.])
for i in range(41,144):
    f=frames[i]
    d=cv2.absdiff(f,bg).max(axis=2)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    white=(hsv[...,1]<80)&(hsv[...,2]>140)
    m=((d>35)&white).astype(np.uint8)
    win=np.zeros_like(m); x0=int(prev[0]-130); y0=int(prev[1]-200)
    win[max(y0,0):y0+400, max(x0,0):x0+200]=1
    if i<49: win[:, :]=0; win[300:950, 1250:1720]=1  # avoid hand at right
    m=m*win
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    ks=[k for k in range(1,n) if 700<st[k,4]<9000]
    if not ks: rows.append((i,np.nan,np.nan,0,0,0,*cam[i][:2])); continue
    k=max(ks,key=lambda k:st[k,4])
    ys,xs=np.nonzero(lab==k)
    cx,cy=xs.mean(),ys.mean()
    rows.append((i,cx,cy,st[k,2],st[k,3],st[k,4],*cam[i][:2]))
    prev=np.array([cx,cy])
T=np.array(rows)
np.savetxt(OUT+'ball_track_full.txt',T,fmt='%.2f',header='frame cx cy w h area camdx camdy (cam rel f75)')
for r in T: print('%d x%.1f y%.1f w%d h%d a%d cam(%.2f,%.2f)'%tuple(r))
