import cv2,numpy as np,sys
v=sys.argv[1]
c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4')
rows=[]
i=0
prev=None
while True:
    ok,im=c.read()
    if not ok or i>100: break
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    H,S,V=hsv[...,0].astype(int),hsv[...,1].astype(int),hsv[...,2].astype(int)
    m=((H>=5)&(H<=25)&(S>50)&(V>40)).astype(np.uint8)
    m[:, :450]=0; m[:,1000:]=0; m[500:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    x,y,w,h,A=st[k]
    # column profile in central columns for top/bottom edges
    cols=m[:,600:850]
    prof=cols.mean(1)
    ys=np.nonzero(prof>0.5)[0]
    diff=0.0 if prev is None else float(np.abs(im.astype(int)-prev).mean())
    prev=im.astype(int)
    rows.append((i,x,y,w,h,A,cen[k][0],cen[k][1],ys.min(),ys.max(),diff))
    i+=1
for r in rows: print(*[round(float(v),2) for v in r])
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/%s_box.npy'%v,np.array(rows,float))
