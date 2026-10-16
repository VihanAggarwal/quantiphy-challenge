import cv2, numpy as np, sys
v=sys.argv[1] if len(sys.argv)>1 else 'captured_0008'
F='/home/user/quantiphy-challenge/research/next/labaudit/0008/frames/'
for i in range(49):
    im=cv2.imread(f'{F}{v}_f{i:02d}.png')
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]<=18)|(hsv[...,0]>=170))&(hsv[...,1]>120)&(hsv[...,2]>90)
    m=m.astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    ys,xs=np.nonzero(lab==k)
    # min enclosing circle and equiv radius
    (cx,cy),rr=cv2.minEnclosingCircle(np.stack([xs,ys],1).astype(np.float32))
    print(f'{i:2d} t={i/24:.3f} bbox x{x}-{x+w} y{y}-{y+h} w{w} h{h} area{a} req{np.sqrt(a/np.pi):.1f} cen({xs.mean():.1f},{ys.mean():.1f}) mec({cx:.1f},{cy:.1f},{rr:.1f})')
