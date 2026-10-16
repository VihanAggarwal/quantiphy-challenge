import cv2, numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0010/frames'
f=711.0; cx0=640.0; cy0=360.0
rows=[]
for i in range(49):
    im=cv2.imread(f'{d}/fs_{i:02d}.png')
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    h,sa,v=cv2.split(hsv)
    m=(((h<14)|(h>172))&(sa>110)&(v>90)).astype(np.uint8)
    m[690:,:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    ys,xs=np.nonzero(lab==k)
    sx=xs.std(); sy=ys.std()
    # row widths
    widths=[ (xs[ys==y].max()-xs[ys==y].min()+1) for y in np.unique(ys)]
    cols=[ (ys[xs==x].max()-ys[xs==x].min()+1) for x in np.unique(xs)]
    rows.append(dict(f=i,u=xs.mean(),v=ys.mean(),Dx=4*sx,Dy=4*sy,wmax=max(widths),hmax=max(cols),deq=2*np.sqrt(len(xs)/np.pi)))
for r in rows: print(f"{r['f']:2d} t={r['f']/24:.3f} u={r['u']:6.1f} v={r['v']:6.1f} Dx={r['Dx']:5.1f} Dy={r['Dy']:5.1f} wmax={r['wmax']} hmax={r['hmax']} deq={r['deq']:5.1f}")
json.dump(rows,open('/home/user/quantiphy-challenge/research/next/labaudit/0010/track_s.json','w'),default=float)
