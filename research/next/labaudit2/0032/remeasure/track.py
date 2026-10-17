import cv2, numpy as np, json
res=[]
for i in range(49):
    f=cv2.imread('frames/f%02d.png'%i)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    H,S,V=[hsv[...,k].astype(int) for k in range(3)]
    roi=np.zeros(S.shape,bool); roi[380:520,450:980]=True
    # white ball: low saturation, high value
    w=(S<50)&(V>190)&roi
    # yellow ball
    y=(H>20)&(H<45)&(S>90)&(V>120)&roi
    out={'i':i}
    for name,m in [('w',w),('y',y)]:
        m8=m.astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m8)
        if n>1:
            k=1+np.argmax(st[1:,4])
            out[name]=[float(cen[k][0]),float(cen[k][1]),int(st[k,4]),int(st[k,0]),int(st[k,1]),int(st[k,2]),int(st[k,3])]
    res.append(out)
    print(out)
json.dump(res,open('track_color.json','w'))
