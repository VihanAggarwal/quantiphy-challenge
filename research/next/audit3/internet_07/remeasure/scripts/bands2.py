import json,numpy as np
e=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/edges3.json'))
fr=np.arange(61,80)
bands=[(650,690),(690,730),(730,770),(770,810),(810,850),(895,925),(925,955),(955,985)]
fps=30.
def fit(x,f,deg,lo,hi):
    m=(f>=lo)&(f<=hi)&~np.isnan(x)
    t=(f[m]-65)/fps; p=np.polyfit(t,x[m],deg); dp=np.polyder(p)
    return p,dp,np.sqrt(np.mean((x[m]-np.polyval(p,t))**2))
allc={}
for (r0,r1) in bands:
    L=[];R=[]
    for i in fr:
        A=np.array(e[str(i)],float); m=(A[:,0]>=r0)&(A[:,0]<r1)
        L.append(np.nanmedian(A[m,1])); R.append(np.nanmedian(A[m,3]))
    L=np.array(L);R=np.array(R); c=(L+R)/2; w=R-L
    allc[(r0,r1)]=c
    p,dp,rms=fit(c,fr,3,61,79)
    v=[np.polyval(dp,(f-65)/fps) for f in (60,69)]
    p2,dp2,rms2=fit(c,fr,2,61,72)
    v2=[np.polyval(dp2,(f-65)/fps) for f in (60,69)]
    print('%d-%d cubic61-79 rms %.2f v60 %.0f v69 %.0f a %.0f R=%.2f | quad61-72 rms %.2f v60 %.0f a %.0f R=%.2f | w %s'%(r0,r1,rms,v[0],v[1],(v[1]-v[0])/.3,v[0]/(v[1]-v[0]),rms2,v2[0],(v2[1]-v2[0])/.3,v2[0]/(v2[1]-v2[0]), np.round(w[[0,4,9,14,18]],0)))
ks=list(allc)
M=np.array([allc[k] for k in ks])
print('band-to-band center differences vs mean (px):')
mean=np.nanmean(M,0)
for k,row in zip(ks,M): print(k,np.round(row-mean,1))
json.dump({'%d_%d'%k:v.tolist() for k,v in allc.items()},open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/bands2.json','w'))
