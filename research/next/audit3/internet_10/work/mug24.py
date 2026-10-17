import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0024.mp4')
k=0
prev=None
while True:
    ok,f=c.read()
    if not ok: break
    s=cv2.resize(f,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
    g=cv2.cvtColor(s,cv2.COLOR_BGR2GRAY)
    # coffee: very dark region in right part (exclude notebook top-right: restrict y>500 half-res)
    roi=g[480:1080,1100:1920]
    m=(roi<45).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        j=1+np.argmax(st[1:,4]); cx,cy=cen[j][0]*2+2200,cen[j][1]*2+960
        x,y,w,h,a=st[j]
        sp='' if prev is None else ' step %.1f'%np.hypot(cx-prev[0],cy-prev[1])
        print(k,'coffee c=(%.0f,%.0f) w%d h%d a%d'%(cx,cy,w*2,h*2,a*4)+sp)
        prev=(cx,cy)
    k+=1
