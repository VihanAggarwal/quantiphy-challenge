import cv2,numpy as np,sys
v=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2:6])
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
acc=[]
while True:
    ok,f=c.read()
    if not ok: break
    acc.append(f[y0:y1,x0:x1].astype(float))
m=np.median(np.array(acc),0)
g=m.mean(2)
print('lum range',g.min(),g.max())
thr=(np.percentile(g,10)+np.percentile(g,90))/2
mask=((g<thr)|((m[...,2]>150)&(m[...,1]>150)&(m[...,0]<120))).astype(np.uint8)  # dark card or yellow sticker
cs,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
cnt=max(cs,key=cv2.contourArea)
hull=cv2.convexHull(cnt)
ap=cv2.approxPolyDP(hull,2.0,True).reshape(-1,2)+[x0,y0]
print('area',cv2.contourArea(cnt),'quad',ap.tolist())
rect=cv2.minAreaRect(cnt); print('minAreaRect',rect)
for y in range(0,y1-y0,3):
    xs=np.where(mask[y])[0]
    if len(xs): print(y0+y,x0+xs.min(),x0+xs.max(),xs.max()-xs.min()+1)
