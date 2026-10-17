import json,numpy as np
from lsq import least_squares
e=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/edges3.json'))
YREF=800
def robline(y,x,thr=2.0):
    m=~np.isnan(x)
    y=y[m]; x=x[m]
    if len(x)<8: return np.nan,np.nan,0
    w=np.ones_like(x)
    for _ in range(10):
        A=np.vstack([np.ones_like(y),(y-YREF)]).T
        p=np.linalg.lstsq(A*w[:,None],x*w,rcond=None)[0]
        r=x-A@p; s=1.4826*np.median(abs(r))+0.3
        w=(abs(r)<thr*s).astype(float)
    return p[0],p[1],int(w.sum())
rows={}
for k in sorted(e,key=int):
    A=np.array(e[k],float); y=A[:,0]
    mL=(y>=650)&(y<=900)&(A[:,2]>20)
    mR=(((y>=650)&(y<=785))|((y>=885)&(y<=950)))&(A[:,4]>20)
    mRlo=((y>=885)&(y<=950))&(A[:,4]>20)
    mRup=((y>=650)&(y<=785))&(A[:,4]>20)
    L=robline(y[mL],A[mL,1]); R=robline(y[mR],A[mR,3]); Ru=robline(y[mRup],A[mRup,3]); 
    rows[int(k)]=(L,R,Ru)
    print(k,'L %8.2f slope %+.3f n%3d | R %8.2f slope %+.3f n%3d | Rup-only %8.2f slope %+.3f | c %8.2f w %6.2f'%(*L,*R,Ru[0],Ru[1],(L[0]+R[0])/2,R[0]-L[0]))
fr=np.array(sorted(rows))
L=np.array([rows[i][0][0] for i in fr]); R=np.array([rows[i][1][0] for i in fr])
c=(L+R)/2; w=R-L
ok=(fr>=63)&~np.isnan(c)
def res(p): return p[0]*np.sqrt(1+((c[ok]-p[1])/p[2])**2)-w[ok]
p=least_squares(res,[420,960,1600]).x
print('width model',np.round(p,1),'rms',np.sqrt(np.mean(res(p)**2)).round(2), np.round(res(p),1))
cR=R-p[0]/2
for _ in range(20): cR=R-p[0]*np.sqrt(1+((cR-p[1])/p[2])**2)/2
cL=L+p[0]/2
for _ in range(20): cL=L+p[0]*np.sqrt(1+((cL-p[1])/p[2])**2)/2
json.dump(dict(fr=fr.tolist(),L=L.tolist(),R=R.tolist(),c=c.tolist(),cR=cR.tolist(),cL=cL.tolist(),p=p.tolist()),open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/linefit.json','w'))
for i,a,b,cc in zip(fr,c,cR,cL): print(i,'c %.2f cR %.2f cL %.2f'%(a,b,cc))
