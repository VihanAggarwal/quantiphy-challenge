from load import load
import numpy as np, cv2, json
fr=load(gray=False)
N=len(fr)
bgg=np.median(np.stack([cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr[96:114:2]]),axis=0).astype(np.float32)
def coarse(i):
    g=cv2.cvtColor(fr[i],cv2.COLOR_BGR2GRAY).astype(np.float32)
    d=np.abs(g-bgg)[700:860]
    col=(d>25).mean(0)
    xs=np.where(col>0.7)[0]
    return xs
rowsL=list(range(660,860,4))
rowsR=list(range(660,860,4))+list(range(920,1040,4))
def edge_rows(i,xl0,xr0,win=45):
    f=cv2.GaussianBlur(fr[i].astype(np.float32),(0,0),1.5)
    gx=np.abs(cv2.Sobel(f,cv2.CV_32F,1,0,ksize=3)).sum(2)
    out={'L':[],'R':[]}
    for side,rows,x0 in (('L',rowsL,xl0),('R',rowsR,xr0)):
        for r in rows:
            p=gx[r-2:r+3].mean(0)
            a=int(max(1,x0-win)); b=int(min(1918,x0+win))
            if b-a<10: continue
            seg=p[a:b]; k=int(np.argmax(seg))
            if k==0 or k==len(seg)-1: continue
            y0,y1,y2=seg[k-1],seg[k],seg[k+1]; d=0.5*(y0-y2)/(y0-2*y1+y2)
            out[side].append((r,a+k+d,y1))
    return out
res={}
for i in range(54,86):
    xs=coarse(i)
    if len(xs)<50: continue
    xl0,xr0=np.percentile(xs,1),np.percentile(xs,99)
    o=edge_rows(i,xl0,xr0)
    # second pass: re-center on median
    L=np.array(o['L']); R=np.array(o['R'])
    xl1=np.median(L[:,1]) if len(L) else xl0; xr1=np.median(R[:,1]) if len(R) else xr0
    o=edge_rows(i,xl1,xr1,win=25)
    L=np.array(o['L']); R=np.array(o['R'])
    res[i]={'L':L.tolist(),'R':R.tolist()}
    def rs(A):
        if len(A)==0: return 'nan'
        return '%.2f mad %.2f n %d str %.0f'%(np.median(A[:,1]),np.median(np.abs(A[:,1]-np.median(A[:,1]))),len(A),np.median(A[:,2]))
    print(i,'coarse %d %d'%(xl0,xr0),'| L',rs(L),'| R',rs(R))
json.dump(res,open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/edges.json','w'))
