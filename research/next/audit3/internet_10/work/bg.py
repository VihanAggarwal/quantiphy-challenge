import cv2,numpy as np,sys
clip=sys.argv[1]; f0,f1=int(sys.argv[2]),int(sys.argv[3]); bgr=sys.argv[4]  # bg frames "a:b"
thr=int(sys.argv[5]) if len(sys.argv)>5 else 30
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/internet_{clip}.mp4')
frames={}
i=0
b0,b1=map(int,bgr.split(':'))
need=set(range(f0,f1+1))|set(range(b0,b1+1,2))
while True:
    ok,f=cap.read()
    if not ok: break
    if i in need: frames[i]=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.int16)
    i+=1
bg=np.median(np.stack([frames[k] for k in range(b0,b1+1,2)]),axis=0)
for k in range(f0,f1+1):
    d=np.abs(frames[k]-bg)>thr
    d=cv2.morphologyEx(d.astype(np.uint8),cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(d)
    if n<2: print(k,'none'); continue
    j=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[j]
    print(k, 'bbox x%d-%d y%d-%d area %d cen %.1f %.1f'%(x,x+w,y,y+h,a,cen[j][0],cen[j][1]))
