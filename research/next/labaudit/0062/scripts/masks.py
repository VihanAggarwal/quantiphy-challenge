import cv2, numpy as np, json
from common import *
X=load('x')
res=[]
for n,f in enumerate(X):
    g=f.max(axis=2)
    m=(g>40).astype(np.uint8)
    m[690:,:]=0  # watermark bottom area? check
    k,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    comps=[(int(st[i,4]),[int(v) for v in st[i,:4]],[round(float(c),1) for c in cen[i]]) for i in range(1,k) if st[i,4]>150]
    comps.sort(key=lambda c:-c[0])
    res.append(comps)
    if n%6==0 or n in (33,34,35): print(n, comps)
json.dump(res,open(O+'xcomps.json','w'))
