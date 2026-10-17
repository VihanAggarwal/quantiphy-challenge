import cv2,numpy as np,sys
v=sys.argv[1]; thr=float(sys.argv[2]) if len(sys.argv)>2 else 20
c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4')
F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(im)
F=np.array(F)
bg=np.median(F,axis=0).astype(np.float32)
for i,im in enumerate(F):
    d=np.abs(im.astype(np.float32)-bg).max(axis=2)
    m=(d>thr).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    print(i,x,y,w,h,a, round(x+w/2,1), round(y+h/2,1))
