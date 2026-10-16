import cv2,numpy as np,sys
src=sys.argv[1]
bg=np.median([cv2.imread('frames/%s_%02d.png'%(src,i)).astype(np.float32) for i in range(34,49)],axis=0)
prev=None
for i in range(0,27):
    f=cv2.imread('frames/%s_%02d.png'%(src,i)).astype(np.float32)
    d=np.abs(f-bg).sum(2)
    win=np.zeros_like(d); 
    if prev is None: prev=(545,296)
    x0,y0=int(prev[0]),int(prev[1])
    win[max(0,y0-35):y0+55, x0-40:x0+40]=1
    d=d*win
    m=(d>45).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    yy,xx=np.nonzero(lab==k)
    prev=(xx.mean(),yy.mean())
    print(i,'bbox',x,y,w,h,'area',a,'cen %.1f %.1f'%prev,'bbmid %.1f %.1f'%(x+(w-1)/2,y+(h-1)/2))
