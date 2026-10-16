import cv2, numpy as np
fr='/home/user/quantiphy-challenge/research/next/labaudit/0029/frames/'
for r in ['0','x']:
    print('render',r)
    for i in range(0,49):
        f=cv2.imread(fr+f'r{r}_{i:02d}.png')
        hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
        m=cv2.inRange(hsv,(22,90,90),(45,255,255))
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: print(i,'none'); continue
        k=1+np.argmax(st[1:,4])
        x,y,w,h,a=st[k]
        print(i, 'cx=%.1f cy=%.1f w=%d h=%d area=%d eqd=%.1f'%(cen[k][0],cen[k][1],w,h,a,2*np.sqrt(a/np.pi)))
