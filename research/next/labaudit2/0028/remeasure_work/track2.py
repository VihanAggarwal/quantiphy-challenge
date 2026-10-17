import cv2, numpy as np, sys, json
v = sys.argv[1] if len(sys.argv)>1 else 'captured_0028x'
c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
res=[]
prev=(719,310)
for i,f in enumerate(fr):
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=((hsv[...,1]<70)&(hsv[...,2]>140)).astype(np.uint8)
    m[690:,:]=0
    m[:, :650]=0; m[:, 850:]=0; m[440:,:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None
    for k in range(1,n):
        if st[k,4]<40: continue
        d=np.hypot(cen[k,0]-prev[0],cen[k,1]-prev[1])
        if best is None or d<best[0]: best=(d,k)
    k=best[1]
    x,y,w,h,a=st[k]
    ys,xs=np.nonzero(lab==k)
    # width per row: median of row widths in central rows
    rows={}
    for yy,xx in zip(ys,xs): rows.setdefault(yy,[]).append(xx)
    wr=sorted([max(v)-min(v)+1 for v in rows.values()])
    cols={}
    for yy,xx in zip(ys,xs): cols.setdefault(xx,[]).append(yy)
    hc=sorted([max(v)-min(v)+1 for v in cols.values()])
    cx,cy=cen[k]
    prev=(cx,cy)
    res.append(dict(i=i,cx=float(cx),cy=float(cy),w=int(w),h=int(h),area=int(a),wmax=int(wr[-1]),hmax=int(hc[-1])))
    print(i, f'{cx:7.2f} {cy:7.2f}  bbox {w}x{h} area {a}  maxrowW {wr[-1]} maxcolH {hc[-1]}')
json.dump(res,open(f'research/next/labaudit2/0028/remeasure_work/track_{v}.json','w'))
