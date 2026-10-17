import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
vid=sys.argv[1]
F=frames(vid,n=49)
np.set_printoptions(suppress=True,precision=2,linewidth=170)
recs=[]
for k in range(len(F)):
    f=F[k].astype(np.int16)
    d=(255*3-f.sum(axis=2))
    out=[]
    for thr in (40,120,250):
        m=(d>thr).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        comps=[(st[i],cen[i]) for i in range(1,n) if st[i][4]>100]
        comps.sort(key=lambda c:c[0][0])
        out.append(comps)
    recs.append(out)
# identify objects by area at thr index 1: two big (brown left, white right), one small rabbit
def pick(k,ti):
    comps=recs[k][ti]
    big=[c for c in comps if c[0][4]>3000]; small=[c for c in comps if 300<c[0][4]<=3000]
    big.sort(key=lambda c:c[0][0])
    return (big[0] if big else None),(big[-1] if len(big)>1 else None),(max(small,key=lambda c:c[0][4]) if small else None)
for ti,thr in enumerate((40,120,250)):
    rows={'brown':[],'white':[],'rabbit':[]}
    for k in range(len(F)):
        b,w,r=pick(k,ti)
        for nm,c in (('brown',b),('white',w),('rabbit',r)):
            if c is not None:
                s,cc=c; rows[nm].append((k,s[0],s[0]+s[2]-1,s[2],s[1],s[1]+s[3]-1,s[3],cc[0],cc[1],s[4]))
    print('--- thr',thr)
    for nm,A in rows.items():
        A=np.array(A,float); kk=A[:,0]
        print(f'{nm:6s} n{len(A)} cx_slope {np.polyfit(kk,A[:,7],1)[0]:.3f} xmin_sl {np.polyfit(kk,A[:,1],1)[0]:.3f} xmax_sl {np.polyfit(kk,A[:,2],1)[0]:.3f} | W med {np.median(A[:,3]):.1f} mean {A[:,3].mean():.1f} p90 {np.percentile(A[:,3],90):.1f} | H med {np.median(A[:,6]):.1f} p90 {np.percentile(A[:,6],90):.1f} | bottom med {np.median(A[:,5]):.1f} max {A[:,5].max():.0f} | top med {np.median(A[:,4]):.1f}')
