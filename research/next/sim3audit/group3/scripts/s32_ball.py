import cv2, numpy as np, json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0032_segmented.mp4')
i=0; rows=[]
while True:
    ok,f=c.read()
    if not ok: break
    g=f.astype(int)
    m=((255*3-g.sum(2))>60).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a>200 and w<60 and h<60:
            ys,xs=np.nonzero(lab==k)
            # subpixel: weighted by darkness
            wgt=(255*3-g[ys,xs].sum(1))/765.
            cx=(xs*wgt).sum()/wgt.sum(); cy=(ys*wgt).sum()/wgt.sum()
            # radius from area (weighted)
            r=np.sqrt(wgt.sum()/np.pi)
            rows.append(dict(f=i,x=int(x),y=int(y),w=int(w),h=int(h),a=int(a),cx=float(cx),cy=float(cy),r=float(r)))
    i+=1
json.dump(rows,open('/home/user/quantiphy-challenge/research/next/sim3audit/group3/s32_ball.json','w'))
for r in rows: print(r['f'],r['x'],r['y'],r['w'],r['h'],r['a'],round(r['cx'],2),round(r['cy'],2),round(2*r['r'],2))
