import cv2,numpy as np,sys
v=sys.argv[1]; thr=float(sys.argv[2]); ylo=int(sys.argv[3]); yhi=int(sys.argv[4])
c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4')
F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(cv2.GaussianBlur(im,(3,3),0)[ylo:yhi])
F=np.array(F)
bg=np.median(F,axis=0).astype(np.float32)
res=[]
for i,im in enumerate(F):
    d=np.abs(im.astype(np.float32)-bg).max(axis=2)
    m=(d>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    # per-row extents to find ball width at widest row
    mk=(lab==k)
    ys=np.where(mk.any(1))[0]
    widths=[(mk[r].nonzero()[0].max()-mk[r].nonzero()[0].min()+1) for r in ys]
    print(i,x,x+w-1,y+ylo,y+h-1+ylo,w,h,a,'maxrowwidth',max(widths))
