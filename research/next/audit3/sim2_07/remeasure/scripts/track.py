import cv2, numpy as np, json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0254.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f.astype(np.float32))
bg=np.median(np.stack(fr[0:12]),axis=0)
res=[]
for i,f in enumerate(fr):
    d=np.abs(f-bg).sum(2)
    hsv=cv2.cvtColor(f.astype(np.uint8),cv2.COLOR_BGR2HSV)
    m=(d>30).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: res.append((i,None)); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    # weighted centroid in a window
    x0,y0=max(0,x-6),max(0,y-6); x1,y1=min(1920,x+w+6),min(1080,y+h+6)
    W=d[y0:y1,x0:x1]; W=np.clip(W-15,0,None)
    yy,xx=np.mgrid[y0:y1,x0:x1]
    cx=(W*xx).sum()/W.sum(); cy=(W*yy).sum()/W.sum()
    res.append((i,dict(bbox=[int(x),int(y),int(w),int(h)],area=int(a),cx=float(cx),cy=float(cy),eqd=float(2*np.sqrt(a/np.pi)),sat=float(hsv[...,1][lab==k].mean()))))
for i,r in res:
    print(i,r)
json.dump(res,open('track0254.json','w'))
