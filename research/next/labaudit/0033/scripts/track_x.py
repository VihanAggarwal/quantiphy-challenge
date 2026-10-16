import cv2, numpy as np, json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0033x.mp4'); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
fr=np.array(fr)
med=np.median(fr,axis=0).astype(np.int16)
res=[]
for i,f in enumerate(fr):
    d=np.abs(f.astype(np.int16)-med).max(axis=2)
    m=(d>40).astype(np.uint8)
    m[690:,:]=0  # caption
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=sorted([(st[k,4],k) for k in range(1,n)],reverse=True)[:3]
    out=[]
    for a,k in comps:
        x,y,w,h=st[k,:4]
        out.append(dict(area=int(a),cx=float(cen[k,0]),cy=float(cen[k,1]),w=int(w),h=int(h),x=int(x),y=int(y)))
    res.append(out)
    print(i, '%.3f'%(i/24), ['a%d c(%.1f,%.1f) %dx%d'%(o['area'],o['cx'],o['cy'],o['w'],o['h']) for o in out])
json.dump(res,open('/home/user/quantiphy-challenge/research/next/labaudit/0033/track_x_raw.json','w'))
