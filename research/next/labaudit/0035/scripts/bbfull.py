import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0035/scripts')
from seg import masks,S
v=sys.argv[1]; dil=int(sys.argv[2]) if len(sys.argv)>2 else 9
fr=np.load(f'{S}/f0035{v}.npy')
tr=json.load(open(f'{S}/tr_{v}.json'))
out={}
for i,f in enumerate(fr):
    green,orange=masks(f)
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    o=cv2.morphologyEx(orange.astype(np.uint8),cv2.MORPH_OPEN,k)
    n,lab,st,cen=cv2.connectedComponentsWithStats(o,8)
    if n<2: continue
    j=1+np.argmax(st[1:,4]); o=(lab==j).astype(np.uint8)
    cs,_=cv2.findContours(o,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    hull=cv2.convexHull(max(cs,key=cv2.contourArea))
    oh=np.zeros_like(o); cv2.drawContours(oh,[hull],-1,1,-1)
    region=cv2.dilate(oh,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*dil+1,2*dil+1)))
    m=((~green).astype(np.uint8))&region
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea)
    (ex,ey),(ma,MA),ang=cv2.fitEllipse(c)
    A=cv2.contourArea(c)
    M=cv2.moments(c)
    out[i]=dict(cx=M['m10']/M['m00'],cy=M['m01']/M['m00'],minor=min(ma,MA),major=max(ma,MA),A=A,hull_minor=min(cv2.fitEllipse(hull)[1]))
    print(i,'%.1f %.1f minor %.1f major %.1f deq %.1f | orange-hull minor %.1f'%(out[i]['cx'],out[i]['cy'],out[i]['minor'],out[i]['major'],np.sqrt(4*A/np.pi),out[i]['hull_minor']))
tr['bbfull']=out
json.dump(tr,open(f'{S}/tr_{v}.json','w'))
