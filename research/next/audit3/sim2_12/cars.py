import cv2, numpy as np, sys, json
p = sys.argv[1]
cap = cv2.VideoCapture(p)
res=[]
i=0
while True:
    ok,f=cap.read()
    if not ok: break
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32)
    bgv=np.median(g)
    sat=hsv[...,1]
    ym=(sat>70)&(hsv[...,0]>15)&(hsv[...,0]<40)
    bwm=(sat<40)&((g>bgv+45)|(g<bgv-70))
    out={}
    for name,m in (('Y',ym),('BW',bwm)):
        m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: out[name]=None; continue
        k=1+np.argmax(st[1:,4])
        # include components near the main one (mirrors) within 30px of bbox
        x,y,w,h,a=st[k]
        sel=[k]
        for j in range(1,n):
            if j==k or st[j][4]<8: continue
            xj,yj,wj,hj,aj=st[j]
            if xj>x-30 and xj+wj<x+w+30 and yj>y-30 and yj+hj<y+h+30: sel.append(j)
        mm=np.isin(lab,sel)
        ys,xs=np.nonzero(mm)
        out[name]=[int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max()),float(xs.mean()),float(ys.mean())]
    res.append(out); i+=1
json.dump(res,open(sys.argv[2],'w'))
for i in [0,1,2,12,23,24,36,47,48,60,71]:
    print(i,res[i])
