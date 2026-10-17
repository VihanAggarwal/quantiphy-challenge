import cv2, numpy as np, sys, json
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
    out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
def redmask(f):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    h,s,v=hsv[...,0].astype(int),hsv[...,1].astype(int),hsv[...,2].astype(int)
    m=((h<=12)|(h>=170))&(s>120)&(v>120)
    return m.astype(np.uint8)
res={}
for v in ['captured_0010','captured_0010s']:
    F=frames(v); rows=[]
    prev=None
    for i,f in enumerate(F):
        m=redmask(f)
        m[650:,:]=0
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        best=None
        for k in range(1,n):
            a=st[k,4]
            if a<80: continue
            cx,cy=cen[k]
            if prev is not None and np.hypot(cx-prev[0],cy-prev[1])>80: continue
            if best is None or a>st[best,4]: best=k
        if best is None: rows.append(None); continue
        cx,cy=cen[best]; a=st[best,4]; x,y,w,h=st[best,:4]
        prev=(cx,cy)
        rows.append([i,float(cx),float(cy),int(a),int(w),int(h),float(np.sqrt(a/np.pi))])
    res[v]=rows
    for r in rows: print(v,r)
json.dump(res,open('track_red.json','w'))
