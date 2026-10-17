import cv2, numpy as np
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
ax=np.load(S+'ax.npy')
prev=None
res=[]
for k in range(len(ax)):
    hsv=cv2.cvtColor(ax[k],cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]<20)|(hsv[...,0]>170))&(hsv[...,1]>100)&(hsv[...,2]>60)
    m=m.astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    if n<2: res.append(None); print(k,None); continue
    i=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[i]
    # circle fit via min enclosing / contour
    cnts,_=cv2.findContours((lab==i).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    (cx,cy),r=cv2.minEnclosingCircle(cnts[0])
    res.append((cen[i][0],cen[i][1],a,w,h))
    step='' if prev is None else '%.1f'%np.hypot(cen[i][0]-prev[0],cen[i][1]-prev[1])
    print(k,'cen=(%.1f,%.1f) a=%d bbox=%dx%d top=%d bottom=%d enc=(%.1f,%.1f,r%.1f) step=%s'%(cen[i][0],cen[i][1],a,w,h,y,y+h,cx,cy,r,step))
    prev=cen[i]
