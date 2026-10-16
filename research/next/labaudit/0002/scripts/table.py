import cv2, numpy as np
f=cv2.imread('frames/f48.png')
hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(int)
H,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
wood=((H>=5)&(H<=30)&(S>40)&(V>60))
wood=cv2.morphologyEx(wood.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8)).astype(bool)
cv2.imwrite('woodmask.png',wood.astype(np.uint8)*255)
def fit(pts):
    pts=np.array(pts,float)
    vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel()
    res=(pts[:,0]-x0)*vy-(pts[:,1]-y0)*vx
    return (vx,vy,x0,y0),np.std(res)
R=[];L=[];Bk=[]
for y in range(325,470):
    xs=np.nonzero(wood[y,600:900])[0]
    if len(xs): R.append((600+xs.max()+0.5,y))
for y in range(400,480):
    xs=np.nonzero(wood[y,400:600])[0]
    if len(xs): L.append((400+xs.min()-0.5,y))
for x in range(670,725):
    ys=np.nonzero(wood[250:400,x])[0]
    if len(ys): Bk.append((x,250+ys.min()-0.5))
for nm,p in [('right',R),('left',L),('back',Bk)]:
    l,s=fit(p); print(nm,l,s, p[0],p[-1])
# front edge: vertical profile of V along columns
for x in [500,550,600,650,700,750]:
    col=V[440:510,x]; print(x,list(col))
