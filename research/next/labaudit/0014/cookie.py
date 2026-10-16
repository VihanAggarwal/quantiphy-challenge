import cv2, numpy as np
for R in ['rs','ro','rx']:
    im=cv2.imread(f'frames/{R}_40.png')
    sub=im[360:420,460:515].astype(float)
    hsv=cv2.cvtColor(im[360:420,460:515],cv2.COLOR_BGR2HSV)
    # cookie: saturated yellow-orange, hue 10-30, sat>90
    m=((hsv[...,0]>=8)&(hsv[...,0]<=28)&(hsv[...,1]>95)&(hsv[...,2]>90)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); m=(lab==k).astype(np.uint8)
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea)
    (x,y),r=cv2.minEnclosingCircle(c)
    el=cv2.fitEllipse(c)
    print(R,'bbox',st[k][:4],'area',m.sum(),'eqdiam',2*np.sqrt(m.sum()/np.pi),'mincirc d',2*r,'ellipse axes',np.round(el[1],1),'centre',np.round([x+460,y+360],1))
    vis=cv2.resize(im[360:420,460:515],None,fx=8,fy=8,interpolation=cv2.INTER_CUBIC)
    cv2.drawContours(vis,[c*8],-1,(255,0,0),1)
    cv2.imwrite(f'cookie_{R}.png',vis)
