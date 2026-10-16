import cv2, numpy as np
from extract import load
def comps(fr,i):
    f=fr[i]
    nonwhite=(f.astype(int).min(axis=2)<200); nonwhite[650:,1000:]=False
    n,lab,st,cen=cv2.connectedComponentsWithStats(nonwhite.astype(np.uint8))
    order=np.argsort(-st[1:,4])+1
    if len(order)>1 and st[order[1]][4]>1500:
        k=order[1]; m=(lab==k)
        ys,xs=np.nonzero(m)
        return dict(cx=xs.mean(),cy=ys.mean(),top=ys.min(),bot=ys.max(),l=xs.min(),r=xs.max(),a=m.sum())
    return None
fr=load('x')
for name,rng in [('toss1',range(17,23)),('toss2',range(53,59))]:
    T=[];D=[]
    for i in rng:
        c=comps(fr,i); T.append(i); D.append(c)
        print(name,i,{k:round(float(v),1) for k,v in c.items()})
    T=np.array(T,float)
    for key in ['cy','top','bot','cx']:
        y=np.array([d[key] for d in D],float)
        for sub in [slice(0,None),slice(1,None),slice(0,-1),slice(1,-1)]:
            p=np.polyfit(T[sub],y[sub],2); a=2*p[0]
            res=y[sub]-np.polyval(p,T[sub])
            print(f'  {key} frames {int(T[sub][0])}-{int(T[sub][-1])}: a={a:.2f} px/fr^2  apex t={-p[1]/(2*p[0]):.2f} rms={res.std():.2f}')
