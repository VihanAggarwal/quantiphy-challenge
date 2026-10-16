import cv2, numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0010/frames'
res={}
for s in ['s','X','o']:
    rows=[]
    for i in range(49):
        im=cv2.imread(f'{d}/f{s}_{i:02d}.png')
        hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        h,sa,v=cv2.split(hsv)
        # red/orange: hue <15 or >170, sat>120
        m=(((h<14)|(h>172))&(sa>110)&(v>90)).astype(np.uint8)
        m[690:,:]=0
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<=1: rows.append(None); continue
        k=1+np.argmax(st[1:,4])
        x,y,w,hh,a=st[k]
        cx,cy=cen[k]
        # equivalent diameter
        rows.append(dict(f=i,cx=float(cx),cy=float(cy),w=int(w),h=int(hh),area=int(a),deq=float(2*np.sqrt(a/np.pi))))
    res[s]=rows
    print(s)
    for r in rows:
        if r: print(f"{r['f']:2d} t={r['f']/24:.3f} cx={r['cx']:7.1f} cy={r['cy']:6.1f} w={r['w']:3d} h={r['h']:3d} deq={r['deq']:5.1f}")
json.dump(res,open('/home/user/quantiphy-challenge/research/next/labaudit/0010/track.json','w'))
