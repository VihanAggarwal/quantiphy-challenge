import cv2, numpy as np, json, sys
# white-ball track in each render: centroid, bbox, mid-row width; restricted to a window around the ball
out={}
for V in ['captured_0028x','captured_0028','captured_0028s']:
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{V}.mp4'); F=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        F.append(f)
    prev=(720,300); rows=[]
    for i,f in enumerate(F):
        x0,y0=int(prev[0])-60,int(prev[1])-80
        x0=max(x0,0); y0=max(y0,0)
        c=f[y0:y0+170,x0:x0+120].astype(int)
        hsv=cv2.cvtColor(f[y0:y0+170,x0:x0+120],cv2.COLOR_BGR2HSV).astype(int)
        m=(hsv[:,:,2]>170)&(hsv[:,:,1]<60)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
        if n<2: rows.append(None); continue
        k=1+np.argmax(st[1:,4])
        if st[k,4]<40: rows.append(None); continue
        mk=lab==k
        ys,xs=np.nonzero(mk)
        cx,cy=xs.mean()+x0,ys.mean()+y0
        bx,by,bw,bh=st[k,:4]
        # widths per row -> median of central rows
        wr=[mk[r].sum() for r in range(by,by+bh)]
        wmid=np.median(sorted(wr)[-max(3,bh//3):])
        rows.append(dict(i=i,cx=round(cx,2),cy=round(cy,2),top=int(by+y0),bot=int(by+bh-1+y0),left=int(bx+x0),right=int(bx+bw-1+x0),w=float(wmid),h=int(bh),area=int(st[k,4])))
        prev=(cx,cy)
    out[V]=rows
json.dump(out,open('/home/user/quantiphy-challenge/research/next/labaudit2/0028/track.json','w'),indent=0)
for i in range(49):
    s=f'{i:2d}'
    for V in out:
        r=out[V][i]
        s+= '  |  none' if r is None else f"  | c=({r['cx']:6.1f},{r['cy']:6.1f}) tb={r['top']}-{r['bot']} lr={r['left']}-{r['right']} w={r['w']:.0f} h={r['h']}"
    print(s)
