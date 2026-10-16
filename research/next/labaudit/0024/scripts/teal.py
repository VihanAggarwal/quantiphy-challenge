import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/'
fr=sys.argv[1] if len(sys.argv)>1 else 'x10'
im=cv2.imread(D+f'frames/{fr}.png')
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
b,g,r=[im[...,i].astype(int) for i in range(3)]
teal=(b-r>18)&(g-r>12)&(g>120)
teal=teal.astype(np.uint8)
n,lab,st,cen=cv2.connectedComponentsWithStats(teal)
k=1+np.argmax(st[1:,4]); m=(lab==k).astype(np.uint8)
print(fr,'teal blob area',st[k,4],'bbox',st[k,:4],'centroid',cen[k].round(1))
cnt,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cnt,key=cv2.contourArea)
hull=cv2.convexHull(c)
for eps in [2,3,4]:
    ap=cv2.approxPolyDP(hull,eps,True).reshape(-1,2); print(' approx eps',eps,ap.tolist())
# per-row extents
ys=np.where(m.any(1))[0]
for y in range(ys.min(),ys.max()+1,3):
    xs=np.where(m[y])[0]; print('  row',y,xs.min(),xs.max())
vis=im.copy(); vis[m>0]=(0.5*vis[m>0]+[0,0,127]).astype(np.uint8)
x0,y0,x1,y1=st[k,0]-15,st[k,1]-15,st[k,0]+st[k,2]+15,st[k,1]+st[k,3]+15
cv2.imwrite(D+f'teal_{fr}.png',cv2.resize(vis[y0:y1,x0:x1],None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST))
