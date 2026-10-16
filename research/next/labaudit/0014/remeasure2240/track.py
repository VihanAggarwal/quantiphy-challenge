import cv2,numpy as np,sys
src=sys.argv[1] if len(sys.argv)>1 else 'captured_0014'
bg=np.median([cv2.imread('frames/%s_%02d.png'%(src,i)).astype(np.float32) for i in range(32,49)],axis=0)
res=[]
for i in range(0,30):
    f=cv2.imread('frames/%s_%02d.png'%(src,i)).astype(np.float32)
    d=np.abs(f-bg).sum(2)
    d[:250,:]=0; d[:, :400]=0; d[:,760:]=0; d[560:,:]=0
    m=(d>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4])
        x,y,w,h,a=st[k]
        # weighted centroid
        ys,xs=np.nonzero(lab==k); wts=d[ys,xs]
        print(i, 'bbox',x,y,w,h,'area',a,'cen %.1f %.1f'%tuple(cen[k]), 'wcen %.1f %.1f'%((xs*wts).sum()/wts.sum(),(ys*wts).sum()/wts.sum()))
    else: print(i,'none')
