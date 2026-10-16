import cv2, numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0030/frames'
res={}
for r in ['x','s','o']:
    tr=[]
    for i in range(49):
        im=cv2.imread(f'{d}/{r}_{i:02d}.png')
        hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        h,s,v=hsv[...,0].astype(int),hsv[...,1].astype(int),hsv[...,2].astype(int)
        m=(((h<=12)|(h>=170))&(s>110)&(v>60)).astype(np.uint8)
        m[:300]=0; m[620:]=0  # restrict to table band roughly
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<=1: tr.append(None); continue
        k=1+np.argmax(st[1:,4])
        x,y,w,hh,a=st[k]
        tr.append(dict(cx=float(cen[k][0]),cy=float(cen[k][1]),w=int(w),h=int(hh),a=int(a),x0=int(x),y0=int(y)))
    res[r]=tr
json.dump(res,open('/home/user/quantiphy-challenge/research/next/labaudit/0030/track_red.json','w'),indent=0)
for i in range(49):
    print(i, f'{i/24:.3f}', *[ (f"{t['cx']:.1f},{t['cy']:.1f} {t['w']}x{t['h']} a{t['a']}" if (t:=res[r][i]) else 'None') for r in ['x','s','o']], sep=' | ')
