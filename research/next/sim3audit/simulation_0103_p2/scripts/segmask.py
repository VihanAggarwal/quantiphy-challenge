import cv2, numpy as np, sys
# print bounding boxes of non-white connected components per sampled frame in a segmented clip
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
clip=sys.argv[1]; step=int(sys.argv[2]) if len(sys.argv)>2 else 12
c=cv2.VideoCapture(D+clip+'.mp4'); i=0
while True:
    ok,im=c.read()
    if not ok: break
    if i%step==0:
        g=im.astype(int); m=((255*3-g.sum(2))>40).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
        n,l,st,cen=cv2.connectedComponentsWithStats(m)
        comps=[tuple(s) for s in st[1:] if s[4]>15]
        comps.sort(key=lambda s:-s[4])
        print(i, [(x,y,w,h,a) for x,y,w,h,a in comps[:8]])
    i+=1
