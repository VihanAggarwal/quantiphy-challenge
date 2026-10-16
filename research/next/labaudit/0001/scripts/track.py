import cv2, numpy as np
base='/home/user/quantiphy-challenge/research/next/labaudit/0001/'
res=[]
for i in range(49):
    im=cv2.imread(base+'frames/f%02d.png'%i)
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]>20)&(hsv[...,0]<40)&(hsv[...,1]>100)&(hsv[...,2]>120)).astype(np.uint8)
    m[690:,1000:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    ys,xs=np.nonzero(lab==k)
    # equivalent diameter
    deq=2*np.sqrt(a/np.pi)
    print(i, '%.3f'%(i/24), 'bbox x%d-%d y%d-%d w%d h%d area%d deq%.1f cen(%.1f,%.1f)'%(x,x+w,y,y+h,w,h,a,deq,cen[k][0],cen[k][1]))
