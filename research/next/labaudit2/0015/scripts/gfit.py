import cv2, numpy as np, json
from common import load, cap
def comps(f):
    nonwhite=(f.astype(int).min(axis=2)<200); nonwhite[650:,1000:]=False
    n,lab,st,cen=cv2.connectedComponentsWithStats(nonwhite.astype(np.uint8))
    order=np.argsort(-st[1:,4])+1
    out=[]
    for k in order[:4]:
        if st[k][4]>1200: 
            ys,xs=np.nonzero(lab==k)
            out.append(dict(cx=xs.mean(),cy=ys.mean(),t=ys.min(),b=ys.max(),l=xs.min(),r=xs.max(),a=len(xs)))
    return out
fr=load('x'); res={}
for i in list(range(13,26))+list(range(49,61)):
    cs=comps(fr[i])
    # toy = component whose bbox lies right of x 400 and not the main person (person bbox is huge)
    toy=[c for c in cs if c['a']<9000 and c['l']>395]
    if toy:
        c=toy[0]; res[i]=c
        print(i,cap(i),{k:round(float(v),1) for k,v in c.items()})
    else: print(i,cap(i),'merged', [(int(c['l']),int(c['r']),int(c['t']),int(c['b']),int(c['a'])) for c in cs])
json.dump({i:{k:float(v) for k,v in c.items()} for i,c in res.items()},open('../gtrack_x.json','w'))
