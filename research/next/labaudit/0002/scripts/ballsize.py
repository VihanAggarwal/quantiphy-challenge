import cv2, numpy as np
# segment the orange ball (hue<40, S>50, V>110) near the top of the board while it is still
res=[]
for i in range(0,49):
    f=cv2.imread(f'frames/f{i:02d}.png')
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(int)
    m=((hsv[...,0]<40)&(hsv[...,1]>50)&(hsv[...,2]>110)).astype(np.uint8)
    # restrict to region above table front edge (y<520) and exclude wood? wood hue ~15-20, S ~ 90, V~200 -> overlaps!
    res.append(m)
np.save('scripts/ballmask.npy',np.array(res))
for i in [0,10,20,25,27,28,29,30]:
    m=res[i]
    sub=m[255:310,580:660]
    n,lab,st,cen=cv2.connectedComponentsWithStats(sub)
    k=1+np.argmax(st[1:,4]) if n>1 else None
    if k is None: print(i,'none'); continue
    x,y,w,h,a=st[k]
    ys,xs=np.nonzero(lab==k)
    cnt=np.column_stack([xs,ys]).astype(np.float32)
    (cx,cy),r=cv2.minEnclosingCircle(cnt)
    print(i,'bbox w,h',w,h,'area',a,'eqdiam',2*np.sqrt(a/np.pi),'cen',cx+580,cy+255,'minEncR',r)
