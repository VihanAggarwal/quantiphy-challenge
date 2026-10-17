import cv2,numpy as np,json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0062x.mp4')
i=0; res={}
while True:
    ok,f=c.read()
    if not ok: break
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=((f.min(2)>120)&(hsv[...,1]<60)).astype(np.uint8)
    m[690:,1000:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    mk=(lab==k).astype(np.uint8)
    mk=cv2.morphologyEx(mk,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    cs,_=cv2.findContours(mk,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cnt=max(cs,key=cv2.contourArea); hull=cv2.convexHull(cnt)
    peri=cv2.arcLength(hull,True)
    for eps in np.linspace(0.005,0.1,100):
        ap=cv2.approxPolyDP(hull,eps*peri,True)
        if len(ap)<=4: break
    res[i]=dict(area=int(st[k,4]),bbox=st[k,:4].tolist(),cen=cen[k].tolist(),quad=ap.reshape(-1,2).tolist())
    print(i,st[k],np.round(cen[k],1),ap.reshape(-1,2).tolist())
    if i in (5,20,34,45):
        vis=f.copy(); cv2.polylines(vis,[ap],True,(0,0,255),1)
        x,y,w,h=st[k,:4]; cr=vis[max(0,y-20):y+h+20,max(0,x-20):x+w+20]
        cv2.imwrite(f'wbq{i}.png',cv2.resize(cr,None,fx=2,fy=2))
    i+=1
json.dump(res,open('wbquad.json','w'))
