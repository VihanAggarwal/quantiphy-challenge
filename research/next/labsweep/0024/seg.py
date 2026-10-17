import cv2, numpy as np, json, sys
v=sys.argv[1] if len(sys.argv)>1 else 'captured_0024x'
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
res=[]
for i,f in enumerate(fr):
    b,g,r=[f[...,k].astype(int) for k in range(3)]
    m=((g-r)>15)&((b-r)>12)&(g>130)&(r>90)
    m[:280]=0; m[540:]=0; m[:,:400]=0; m[:,950:]=0
    m=m.astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: res.append(None); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    res.append(dict(i=i,cx=float(cen[k][0]),cy=float(cen[k][1]),x=int(x),y=int(y),w=int(w),h=int(h),a=int(a)))
    print(i,'%.1f %.1f'%tuple(cen[k]),x,y,w,h,a)
json.dump(res,open(f'seg_{v}.json','w'))
