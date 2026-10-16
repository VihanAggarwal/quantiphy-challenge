import cv2, numpy as np, json, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/'
r=sys.argv[1] if len(sys.argv)>1 else 'x'
out={}
for i in range(49):
    im=cv2.imread(d+'frames/%s_%02d.png'%(r,i))
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    H,S,V=[hsv[...,k].astype(int) for k in range(3)]
    roi=np.zeros(V.shape,bool); roi[330:560,300:1100]=True
    yel=(H>=22)&(H<=45)&(S>110)&(V>110)&roi
    wht=(S<55)&(V>165)&roi
    res={}
    for name,m in [('yel',yel),('wht',wht)]:
        m8=m.astype(np.uint8)
        m8=cv2.morphologyEx(m8,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m8)
        if n<2: res[name]=None; continue
        k=1+np.argmax(st[1:,4])
        x,y,w,h,a=st[k]
        res[name]=dict(cx=float(cen[k][0]),cy=float(cen[k][1]),x0=int(x),y0=int(y),w=int(w),h=int(h),area=int(a),
                       bbc=(x+(w-1)/2, y+(h-1)/2), others=[(int(st[j][4]),float(cen[j][0]),float(cen[j][1])) for j in range(1,n) if j!=k and st[j][4]>15])
    out[i]=res
    def f(v): return 'None' if v is None else '(%6.1f,%6.1f) bb %3dx%3d a%4d oth%s'%(v['cx'],v['cy'],v['w'],v['h'],v['area'],v['others'][:2])
    print(i, 'Y', f(res['yel']), '| W', f(res['wht']))
json.dump(out,open(d+'track_%s.json'%r,'w'),default=lambda o: o.tolist() if hasattr(o,'tolist') else int(o))
