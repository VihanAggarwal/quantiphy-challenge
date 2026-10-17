import cv2, numpy as np, sys
# full-res bg-diff extent of butterfly in selected frames; background = median of frames sampled
v=sys.argv[1]; thr=float(sys.argv[2]); frames=list(map(int,sys.argv[3].split(',')))
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
N=int(c.get(cv2.CAP_PROP_FRAME_COUNT))
samp=[]; allf={}
for i in range(N):
    ok,f=c.read()
    if i%4==0: samp.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
    if i in frames: allf[i]=f
bg=np.median(np.array(samp),axis=0).astype(np.float32)
# color bg too
c.set(cv2.CAP_PROP_POS_FRAMES,0)
for i in frames:
    f=allf[i]; g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    d=np.abs(g-bg)
    blue=(hsv[...,0]>90)&(hsv[...,0]<130)&(hsv[...,1]>60)
    m=((d>thr)|(blue&(d>thr/2))).astype(np.uint8)
    if len(sys.argv)>4:
        y0,y1=map(int,sys.argv[4].split(',')); m[:y0]=0; m[y1:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    # robust extent: columns with >=3 mask pixels
    colsum=(lab==k).sum(0); cols=np.nonzero(colsum>=3)[0]
    rowsum=(lab==k).sum(1); rows=np.nonzero(rowsum>=3)[0]
    print(i,'bbox',x,y,w,h,'robust w',cols[-1]-cols[0]+1,'h',rows[-1]-rows[0]+1,'cen %.1f %.1f'%tuple(cen[k]))
