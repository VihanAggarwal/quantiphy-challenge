import cv2, numpy as np
from extract import load
fr=load('x')
res={}
for i in list(range(12,27))+list(range(48,63)):
    f=fr[i]
    nonwhite=(f.astype(int).min(axis=2)<200); nonwhite[650:,1000:]=False
    n,lab,st,cen=cv2.connectedComponentsWithStats(nonwhite.astype(np.uint8))
    order=np.argsort(-st[1:,4])+1
    comps=[(k,st[k],cen[k]) for k in order[:3] if st[k][4]>300]
    out=[]
    for k,s,c in comps:
        out.append(f'bbox x{s[0]}-{s[0]+s[2]} y{s[1]}-{s[1]+s[3]} a{s[4]} c({c[0]:.1f},{c[1]:.1f})')
    print(i, ' | '.join(out))
