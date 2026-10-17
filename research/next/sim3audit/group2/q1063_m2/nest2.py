from load import frames; import numpy as np, cv2
F=frames()
bgl=F[0].astype(int)
pts=[]
for i in range(30,52):
    f=F[i]; x0,x1,y0,y1=120,420,1000,1600
    c=f[y0:y1,x0:x1].astype(int)
    d=np.abs(c-bgl[y0:y1,x0:x1]).sum(2)
    g=c.mean(2)
    m=((d>60)&(g<45)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    pts.append((i,cen[k][0]+x0,cen[k][1]+y0,a,y+y0,y+h+y0,x+x0,x+w+x0))
    print(i,np.round(cen[k]+[x0,y0],1),a,'bbox y',y+y0,y+h+y0,'x',x+x0,x+w+x0)
np.save('nestpts.npy',np.array(pts,float))
