from util import *
fr=frames('simulation_0111')
bg=np.median(np.stack([fr[i] for i in range(100,195,5)]),axis=0).astype(np.float32)
out=[]
for i in list(range(1,80,6))+[200,203,206,209,210]:
    d=np.abs(fr[i].astype(np.float32)-bg).max(axis=2)
    m=(d>30).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    print(i,'bbox x%d-%d y%d-%d w%d h%d A%d cen %.1f %.1f'%(x,x+w,y,y+h,w,h,a,cen[k][0],cen[k][1]))
