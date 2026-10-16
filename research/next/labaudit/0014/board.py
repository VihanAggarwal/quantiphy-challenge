import cv2, numpy as np
for R in ['rs','ro','rx']:
    im=cv2.imread(f'frames/{R}_40.png')
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=((hsv[...,1]<30)&(hsv[...,2]>200)).astype(np.uint8)
    m[:290]=0; m[440:]=0; m[:, :495]=0; m[:, 620:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); m=(lab==k).astype(np.uint8)
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea)
    ap=cv2.approxPolyDP(cv2.convexHull(c),3,True).reshape(-1,2)
    print(R,'area',m.sum(),ap.tolist())
    # fit 4 lines via minAreaRect-free approach: use approxPolyDP with larger eps
    for eps in [5,8]:
        print('  eps',eps,cv2.approxPolyDP(cv2.convexHull(c),eps,True).reshape(-1,2).tolist())
