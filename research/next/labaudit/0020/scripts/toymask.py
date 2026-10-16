import cv2, numpy as np, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
pref=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]
for i in frames:
    im=cv2.imread(d+f'frames/{pref}_f{i:02d}.png')
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
    h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
    # background gray has low saturation; skin hue ~5-18
    for sthr in (50,70,90):
        m=((h>=20)&(h<=60)&(s>sthr)&(v>60)).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: print(i,sthr,'none'); continue
        # merge components near the biggest one
        k=1+np.argmax(st[1:,4]); c=cen[k]
        keep=[j for j in range(1,n) if st[j,4]>15 and np.hypot(*(cen[j]-c))<60]
        mm=np.isin(lab,keep)
        ys,xs=np.nonzero(mm); P=np.c_[xs,ys].astype(float)
        mu=P.mean(0); U,S,Vt=np.linalg.svd(P-mu,full_matrices=False)
        proj=(P-mu)@Vt.T
        L=np.ptp(proj[:,0]); W=np.ptp(proj[:,1])
        print(i,sthr,'area',mm.sum(),'centre',mu.round(1),'axis',Vt[0].round(2),'len %.1f wid %.1f'%(L,W),'bbox',xs.min(),xs.max(),ys.min(),ys.max())
