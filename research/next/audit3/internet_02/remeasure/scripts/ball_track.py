import cv2, numpy as np, sys
V='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0044.mp4'
OUT='/home/user/quantiphy-challenge/research/next/audit3/internet_02/remeasure/'
c=cv2.VideoCapture(V); frames=[]
while True:
    ok,im=c.read()
    if not ok: break
    frames.append(cv2.resize(im,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA))
N=len(frames); print('N',N)
bg=np.median(np.stack(frames[::4]),axis=0).astype(np.uint8)
res=[]
for i,f in enumerate(frames):
    d=cv2.absdiff(f,bg).max(axis=2)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    white=(hsv[...,1]<70)&(hsv[...,2]>150)
    m=((d>40)&white).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    cands=[(st[k,4],cen[k],st[k]) for k in range(1,n) if 150<st[k,4]<2500 and 0.5<st[k,2]/max(st[k,3],1)<2.0]
    cands.sort(key=lambda t:-t[0])
    s=' | '.join(f'a{a} c({cc[0]*2:.1f},{cc[1]*2:.1f}) wh({s_[2]*2},{s_[3]*2})' for a,cc,s_ in cands[:3])
    print(i,s)
