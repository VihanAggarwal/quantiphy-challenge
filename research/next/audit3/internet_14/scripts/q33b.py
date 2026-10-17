import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0033.mp4')
F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(im)
def redmask(im):
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    return (((hsv[...,0]<8)|(hsv[...,0]>172))&(hsv[...,1]>120)&(hsv[...,2]>80)).astype(np.uint8)
# follow the largest red blob after closing
prev=(1530,862)
for f in range(0,47):
    m=redmask(F[f])
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((25,25),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # choose component nearest prev with area>3000
    best=None;bd=1e9
    for i in range(1,n):
        if st[i,4]<3000: continue
        d=np.hypot(cen[i,0]-prev[0],cen[i,1]-prev[1])
        if d<bd: bd=d;best=i
    if best is None: print(f,'none'); continue
    prev=tuple(cen[best])
    x,y,w,h,a=st[best]
    print(f, round(cen[best][0],1), round(cen[best][1],1), 'bbox',x,y,w,h,a)
