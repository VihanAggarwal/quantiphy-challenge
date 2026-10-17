import cv2, numpy as np, sys
vid,out,x0,x1,ref=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
c=cv2.VideoCapture(vid); frames=[]
i=0; rows=[]; bg=None
caps=[]
while True:
    ok,f=c.read()
    if not ok: break
    caps.append(f[:,x0:x1].astype(np.int16))
    i+=1
bg=caps[ref]
for i,f in enumerate(caps):
    d=np.abs(f-bg).sum(2)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
        rows.append((i,x+x0,y,x+w-1+x0,y+h-1,cen[k,0]+x0,cen[k,1],a))
    else: rows.append((i,-1,-1,-1,-1,-1,-1,0))
np.savetxt(out,np.array(rows),fmt='%.2f')
