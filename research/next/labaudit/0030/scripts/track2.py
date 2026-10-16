import cv2, numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0030/frames'
res={}
for r in ['s','o','x']:
    tr=[]; prev=None
    for i in range(49):
        im=cv2.imread(f'{d}/{r}_{i:02d}.png')
        hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        h,s,v=[hsv[...,k].astype(int) for k in range(3)]
        b,g,rr=[im[...,k].astype(int) for k in range(3)]
        m=(((h<=11)|(h>=172))&(s>185)&(v>100)&(rr-g>90)).astype(np.uint8)
        m[:380]=0; m[580:]=0
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        cands=[k for k in range(1,n) if st[k,4]>80]
        if not cands: tr.append(None); continue
        if prev is None: k=max(cands,key=lambda k:st[k,4])
        else: k=min(cands,key=lambda k:np.hypot(*(cen[k]-prev))-0.02*st[k,4])
        x,y,w,hh,a=st[k]
        ys,xs=np.nonzero(lab==k)
        tr.append(dict(cx=float(cen[k][0]),cy=float(cen[k][1]),bx=(x+(x+w-1))/2,by=(y+(y+hh-1))/2,w=int(w),h=int(hh),a=int(a),deq=float(np.sqrt(4*a/np.pi))))
        prev=cen[k]
    res[r]=tr
json.dump(res,open('/home/user/quantiphy-challenge/research/next/labaudit/0030/track2.json','w'),indent=0)
for i in range(49):
    print(i, f'{i/24:.3f}', *[ (f"{t['cx']:.1f},{t['cy']:.1f} bb{t['bx']:.0f},{t['by']:.0f} {t['w']}x{t['h']} d{t['deq']:.0f}" if (t:=res[r][i]) else 'None') for r in ['s','o','x']], sep=' | ')
