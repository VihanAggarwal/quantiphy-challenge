import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
orb=cv2.ORB_create(6000); bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
REF=15
kr,dr=orb.detectAndCompute(g[REF],None)
al=[]
for i in range(30):
    k,d=orb.detectAndCompute(g[i],None); m=bf.match(d,dr)
    src=np.float32([k[x.queryIdx].pt for x in m]); dst=np.float32([kr[x.trainIdx].pt for x in m])
    H,_=cv2.findHomography(src,dst,cv2.RANSAC,1.5)
    al.append(cv2.warpPerspective(fr[i],H,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE))
bgs=np.median(np.stack(al[8:]),axis=0).astype(np.uint8)
lab0=cv2.cvtColor(bgs,cv2.COLOR_BGR2Lab).astype(np.float32)
def matte(i):
    L=cv2.cvtColor(al[i],cv2.COLOR_BGR2Lab).astype(np.float32)
    d=np.sqrt(((L-lab0)**2).sum(axis=2))
    return np.clip(d/45.0,0,1)
t=np.loadtxt('research/next/audit3/internet_11/remeasure/track47d.txt')
pos=dict((int(a),b) for a,b in zip(t[:,0],t[:,1]))
def redtop(x): return 479.7-0.0275*(x-300)
def shift_est(i,j):
    mi=matte(i); mj=matte(j)
    xc=pos[i]; rt=redtop(xc)
    # rows: whole ball but exclude red line band (rt-5..rt+51)
    y0=int(rt-75); y1=int(rt+175)
    rows=[r for r in range(y0,y1) if not (rt-6<=r<=rt+52)]
    A=mi[rows, int(xc-200):int(xc+200)]
    best=None
    guess=pos[j]-pos[i]
    for dy in range(-12,1):
        rows2=[r+dy for r in rows]
        for dx in np.arange(guess-6,guess+6.01,0.25):
            M=np.float32([[1,0,-dx],[0,1,0]])
            Bm=cv2.warpAffine(mj,M,(1920,1080),flags=cv2.INTER_LINEAR)
            B=Bm[rows2, int(xc-200):int(xc+200)]
            e=((A-B)**2).mean()
            if best is None or e<best[0]: best=(e,dx,dy)
    return best
for i in range(9,19):
    e,dx,dy=shift_est(i-1,i+1)
    print('frames %d-%d: dx/2 %.2f dy %d err %.4f'%(i-1,i+1,dx/2,dy,e))
