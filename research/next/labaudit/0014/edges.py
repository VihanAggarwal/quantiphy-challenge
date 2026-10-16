import cv2, numpy as np
im=cv2.imread('frames/rs_40.png').astype(np.float32)
hsv=cv2.cvtColor(im.astype(np.uint8),cv2.COLOR_BGR2HSV)
green=((hsv[...,0]>35)&(hsv[...,0]<90)&(hsv[...,1]>80))
def fitline(pts):
    pts=np.array(pts,float)
    vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel()
    res=np.abs((pts[:,0]-x0)*vy-(pts[:,1]-y0)*vx)
    return np.array([x0,y0]),np.array([vx,vy]),res.mean()
# right edge: for rows y in 318..448, find first green pixel scanning right from x=640 (rightmost table pixel)
R=[]
for y in range(318,446):
    row=green[y,600:760]
    xs=np.where(~row)[0]
    if len(xs): R.append((600+xs.max()+0.5,y))
# left edge: rows 350..495 leftmost non-green pixel from x=400
L=[]
for y in range(352,495):
    row=green[y,400:470]
    xs=np.where(~row)[0]
    if len(xs): L.append((400+xs.min()-0.5,y))
# back edge right part: columns 615..650 topmost non-green from y=290
B=[]
for x in range(612,652):
    col=green[290:340,x]; ys=np.where(~col)[0]
    if len(ys): B.append((x,290+ys.min()-0.5))
# front edge top surface: color change from light wood (top) to dark wood (front face). use brightness gradient
gray=cv2.cvtColor(im.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(float)
Fr=[]
for x in range(440,715):
    col=gray[440:520,x]
    g=np.diff(cv2.GaussianBlur(col.reshape(-1,1),(1,5),0).ravel())
    k=np.argmin(g)  # bright->dark
    Fr.append((x,440+k+0.5))
for name,pts in [('right',R),('left',L),('back',B),('front',Fr)]:
    p,d,r=fitline(pts); print(name,len(pts),p,d,'meanres',round(r,2))
    np.save(f'edge_{name}.npy',np.array([p,d]))
