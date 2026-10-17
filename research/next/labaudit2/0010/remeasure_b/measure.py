import cv2, numpy as np, json
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
T=json.load(open('track_red.json'))['captured_0010s']
out={}
for v in ['captured_0010','captured_0010s']:
    F=frames(v); rows=[]
    for j,f in enumerate(F):
        cx0,cy0=int(T[j][1]),int(T[j][2])
        x0,y0=cx0-45,cy0-45
        win=f[y0:y0+90,x0:x0+90]
        hsv=cv2.cvtColor(win,cv2.COLOR_BGR2HSV)
        h,s,val=[hsv[...,k].astype(int) for k in range(3)]
        m=(((h<=15)|(h>=170))&(s>110)&(val>110)).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        k=1+np.argmax(st[1:,4])
        mk=(lab==k).astype(np.uint8)
        cs,_=cv2.findContours(mk,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        c=max(cs,key=len)
        (ex,ey),(MA,ma),ang=cv2.fitEllipse(c)
        (ccx,ccy),cr=cv2.minEnclosingCircle(c)
        a=mk.sum()
        mo=cv2.moments(mk,True)
        rows.append(dict(j=j,u=x0+mo['m10']/mo['m00'],v=y0+mo['m01']/mo['m00'],ue=x0+ex,ve=y0+ey,
            minor=min(MA,ma),major=max(MA,ma),ang=ang,req=float(np.sqrt(a/np.pi)),w=int(st[k,2]),h=int(st[k,3])))
    out[v]=rows
    print(v)
    for r in rows: print('%2d u=%.1f v=%.1f minor=%.1f major=%.1f req=%.2f w=%d h=%d ang=%.0f'%(r['j'],r['u'],r['v'],r['minor'],r['major'],r['req'],r['w'],r['h'],r['ang']))
json.dump(out,open('ballfit.json','w'))
