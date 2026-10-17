import pickle, numpy as np, sys
vid=sys.argv[1]
R=pickle.load(open(f'{vid}_recs.pkl','rb'))
k=np.arange(49)
# assign by y position: brown top (smallest y), white middle, rabbit (smallest area)
def get(sel):
    out=[]
    for recs in R:
        c=[r for r in recs if sel(r)]
        out.append(c[0] if c else [np.nan]*7)
    return np.array(out,float)
ys=sorted(set(round(r[6]/40) for recs in R for r in recs))
objs={}
for recs in R[:1]:
    for r in recs: print('frame0 obj', np.round(r,1))
return_rows=[]
for name in sys.argv[2:]:
    nm,ylo,yhi=name.split(':'); ylo=float(ylo); yhi=float(yhi)
    A=get(lambda r: ylo<=r[6]<=yhi)
    ok=~np.isnan(A[:,0])
    res={}
    for j,lab in [(5,'cx'),(0,'xmin'),(2,'w')]:
        pass
    p=np.polyfit(k[ok],A[ok,5],1); r=A[ok,5]-np.polyval(p,k[ok])
    xmax=A[:,0]+A[:,2]
    p2=np.polyfit(k[ok],A[ok,0],1); p3=np.polyfit(k[ok],xmax[ok],1)
    loc=np.polyfit(k[16:33],A[16:33,5],1)[0]
    print(f'{nm}: cx slope {p[0]:.3f} (resid {r.std():.2f}) xmin slope {p2[0]:.3f} xmax slope {p3[0]:.3f} local16-32 {loc:.3f} | width med {np.nanmedian(A[:,2]):.1f} p90 {np.nanpercentile(A[:,2],90):.1f} height med {np.nanmedian(A[:,3]):.1f}')
