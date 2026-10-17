import cv2, numpy as np, sys
name=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2:6])
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{name}_segmented.mp4')
i=0; rows=[]
while True:
    ok,f=c.read()
    if not ok: break
    roi=f[y0:y1,x0:x1].astype(int)
    m=(np.abs(roi-255).max(axis=2)>40)
    ys,xs=np.nonzero(m)
    if len(xs)>0:
        rows.append((i,xs.mean()+x0,ys.mean()+y0,xs.min()+x0,xs.max()+x0,ys.min()+y0,ys.max()+y0,len(xs)))
    else: rows.append((i,np.nan,)*1+(np.nan,)*6)
    i+=1
for r in rows: print(' '.join(f'{v:.1f}' if isinstance(v,float) else str(v) for v in r))
