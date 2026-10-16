import cv2, numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0030/frames'
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/track2.json'))
f=711.; c=np.array([640.,360.])
out={}
for r in ['s','o']:
    rows=[]
    for i in range(49):
        t=T[r][i]
        if t is None: rows.append(None); continue
        im=cv2.imread(f'{d}/{r}_{i:02d}.png').astype(int)
        b,g,rr=im[...,0],im[...,1],im[...,2]
        m=((rr-g>80)&(rr>140)).astype(np.uint8)
        x0=int(t['cx']-60); x1=int(t['cx']+60); y0=int(t['cy']-50); y1=int(t['cy']+50)
        sub=np.zeros_like(m); sub[y0:y1,x0:x1]=m[y0:y1,x0:x1]
        n,lab,st,cen=cv2.connectedComponentsWithStats(sub)
        if n<=1: rows.append(None); continue
        # component containing/closest to strict centroid
        k=min(range(1,n),key=lambda k:np.hypot(*(cen[k]-[t['cx'],t['cy']]))-0.01*st[k,4])
        ys,xs=np.nonzero(lab==k)
        # vertical extent in central columns (within +-5 px of median x)
        xm=np.median(xs); sel=np.abs(xs-xm)<=6
        top=ys[sel].min(); bot=ys[sel].max()
        hext=bot-top+1
        # horizontal extent at the centre row band
        yc=(top+bot)/2; selr=np.abs(ys-yc)<=3
        wext=xs[selr].max()-xs[selr].min()+1
        cxb=(xs[selr].max()+xs[selr].min())/2
        cx_,cy_=cxb,yc
        th=np.arctan(np.hypot(cx_-c[0],cy_-c[1])/f)
        rng=f*0.07/hext/np.cos(th)
        rows.append(dict(cx=float(cx_),cy=float(yc),top=int(top),bot=int(bot),h=int(hext),w=int(wext),rng_size=float(rng)))
    out[r]=rows
json.dump(out,open('/home/user/quantiphy-challenge/research/next/labaudit/0030/track3.json','w'))
for i in range(49):
    print(i,f'{i/24:.3f}',*[(f"c=({t['cx']:.1f},{t['cy']:.1f}) top{t['top']} bot{t['bot']} h{t['h']} w{t['w']} rng{t['rng_size']:.3f}" if (t:=out[r][i]) else 'None') for r in ['s','o']],sep=' | ')
