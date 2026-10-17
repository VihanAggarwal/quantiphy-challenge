import json,numpy as np
e=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/edges3.json'))
bands={'top':(560,640),'mid':(690,850),'lo':(900,990),'lo2':(940,1010)}
out={}
for k in sorted(e,key=int):
    A=np.array(e[k],float)
    s=[]
    for b,(r0,r1) in bands.items():
        m=(A[:,0]>=r0)&(A[:,0]<=r1)
        L=A[m&(A[:,2]>15),1]; R=A[m&(A[:,4]>15),3]
        l=np.nanmedian(L) if len(L)>3 else np.nan; r=np.nanmedian(R) if len(R)>3 else np.nan
        ml=np.nanmedian(abs(L-l)) if len(L)>3 else np.nan; mr=np.nanmedian(abs(R-r)) if len(R)>3 else np.nan
        out.setdefault(k,{})[b]=(l,r)
        s.append('%s L %7.2f(%4.1f,%3d) R %7.2f(%4.1f) c %7.2f w %6.2f'%(b,l,ml,np.median(A[m,2]),r,mr,(l+r)/2,r-l))
    print(k,' | '.join(s))
json.dump(out,open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/bands.json','w'))
