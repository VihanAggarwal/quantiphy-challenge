import numpy as np, json, cv2
from load import frames
F=frames(); bg=cv2.imread('bg.png').astype(int); B=json.load(open('birdbox.json'))
# better mask: diff OR darkness near bbox
out=[]
for i,f in enumerate(F):
    b=B[i]; x0,x1,y0,y1=b['x0']-30,b['x1']+30,b['y0']-30,b['y1']+30
    crop=f[y0:y1,x0:x1].astype(int); bc=bg[y0:y1,x0:x1]
    d=np.abs(crop-bc).sum(2)
    gray=crop.mean(2)
    m=((d>45)|((gray<40)&(d>20))).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); mm=(lab==k)
    # include components within 6px
    dil=cv2.dilate(mm.astype(np.uint8),np.ones((13,13),np.uint8))
    for j in range(1,n):
        if j!=k and st[j,4]>5 and (dil[lab==j]).any(): mm|=(lab==j)
    core=cv2.erode(mm.astype(np.uint8),np.ones((9,9),np.uint8))
    ys,xs=np.nonzero(mm); cy_,cx_=np.nonzero(core)
    dark=(gray<35)&mm
    dy,dx=np.nonzero(dark)
    out.append(dict(i=i,x0=int(xs.min()+x0),x1=int(xs.max()+x0),y0=int(ys.min()+y0),y1=int(ys.max()+y0),
        cx=float(xs.mean()+x0),cy=float(ys.mean()+y0),
        corex=float(cx_.mean()+x0) if len(cx_) else None, corey=float(cy_.mean()+y0) if len(cy_) else None,
        area=int(mm.sum())))
    cv2.imwrite(f'masks/m{i:02d}.png', (mm*255).astype(np.uint8)) if False else None
json.dump(out,open('track.json','w'))
for r in out: print(r['i'],r['x0'],r['x1'],r['y0'],r['y1'],round(r['cx'],1),round(r['cy'],1),r['corex'] and round(r['corex'],1),r['corey'] and round(r['corey'],1),r['area'])
