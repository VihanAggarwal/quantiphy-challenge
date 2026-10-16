import cv2, numpy as np
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
D='/home/user/quantiphy-challenge/research/next/labaudit/0022/'
fr=np.load(S+'fr0022x.npy')
for i in [0,24,48]:
    im=fr[i]
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=(im.max(2)>40).astype(np.uint8)
    m[650:,1000:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); mk=(lab==k).astype(np.uint8)
    # remove leg: leg is grey (low saturation)
    tab=((lab==k)&(hsv[...,1]>40)).astype(np.uint8)
    tab=cv2.morphologyEx(tab,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n2,lab2,st2,_=cv2.connectedComponentsWithStats(tab)
    k2=1+np.argmax(st2[1:,4]); tab=(lab2==k2).astype(np.uint8)
    cs,_=cv2.findContours(tab,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea)
    hull=cv2.convexHull(c)
    ap=cv2.approxPolyDP(hull,8,True)
    print(i,'area',cv2.contourArea(c),'approx',ap.reshape(-1,2).tolist())
    np.save(S+f'tabmask_x{i}.npy',tab)
