import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0002.mp4'
c=cv2.VideoCapture(V); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im)
print(len(fr))
g=np.stack([cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr])
bg=np.median(g,axis=0).astype(np.uint8)
# lane lines: max brightness over x in column band, per row
for x0 in [400,1200,1900,2600,3400]:
    band=bg[:,x0-300:x0+300].astype(float)
    prof=np.percentile(band,98,axis=1)
    # smooth and find peaks
    from util import find_peaks
    pk,_=find_peaks(prof,height=prof.mean()+25,distance=150)
    # subpixel centroid
    cents=[]
    for p in pk:
        w=prof[p-6:p+7]-np.median(prof); w=np.clip(w,0,None)
        cents.append((np.arange(p-6,p+7)*w).sum()/w.sum())
    cents=np.array(cents); print(x0,np.round(cents,1),np.round(np.diff(cents),1))
# red mask track
res=[]
for i,f in enumerate(fr):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=(((hsv[...,0]<10)|(hsv[...,0]>170))&(hsv[...,1]>80)&(hsv[...,2]>60)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,l,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: res.append(None); continue
    k=1+np.argmax(st[1:,4])
    # diff mask from bg
    d=cv2.absdiff(g[i],bg)>30
    d=cv2.morphologyEx(d.astype(np.uint8),cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    x,y,w,h,a=st[k]
    # diff region around red blob
    sub=d[max(0,y-150):y+h+150, max(0,x-400):x+w+400]
    n2,l2,st2,c2=cv2.connectedComponentsWithStats(sub)
    res.append((i,cen[k][0],cen[k][1],w,h,a))
    print(i,'red cen %.1f %.1f bbox w %d h %d area %d'%(cen[k][0],cen[k][1],w,h,a))
r=np.array([x for x in res if x is not None])
ok=(r[:,1]>200)&(r[:,1]<3640)
p=np.polyfit(r[ok,0],r[ok,1],1); print('vx px/frame',p[0])
p=np.polyfit(r[ok,0],r[ok,2],1); print('vy px/frame',p[0])
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/internet_01/img/bg0002.jpg',cv2.resize(bg,(960,540)))
