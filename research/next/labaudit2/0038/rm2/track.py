import cv2, numpy as np, sys, json
D='/home/user/quantiphy-challenge/research/next/labaudit2/0038/rm2/'
v=sys.argv[1] if len(sys.argv)>1 else 'x'
fr=[cv2.imread(D+'f%s/%02d.jpg'%(v,i)).astype(np.float32) for i in range(49)]
bg=np.median(np.stack(fr),axis=0)
out=[]
for i,f in enumerate(fr):
    d=np.abs(f-bg).max(axis=2)
    hsv=cv2.cvtColor(f.astype(np.uint8),cv2.COLOR_BGR2HSV)
    white=(hsv[...,2]>170)&(hsv[...,1]<70)
    m=((d>40)&white).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<=1: out.append(None); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    out.append(dict(i=i,cx=float(cen[k][0]),cy=float(cen[k][1]),x=int(x),y=int(y),w=int(w),h=int(h),a=int(a)))
    print(i, '%.1f %.1f'%tuple(cen[k]), x,y,w,h,a)
json.dump(out,open(D+'track_%s.json'%v,'w'))
