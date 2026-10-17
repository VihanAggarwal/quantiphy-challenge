import cv2, numpy as np, sys, json
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
def frames(v):
    c=cv2.VideoCapture(D+v+'.mp4')
    while True:
        ok,f=c.read()
        if not ok: break
        yield f
def sub_edges(prof,thr):
    idx=np.where(prof>thr)[0]
    if len(idx)==0: return np.nan,np.nan
    a,b=idx[0],idx[-1]
    L=a-1+(thr-prof[a-1])/(prof[a]-prof[a-1]) if a>0 else np.nan
    R=b+(prof[b]-thr)/(prof[b]-prof[b+1]) if b<len(prof)-1 else np.nan
    return L,R
out={}
for v in sys.argv[1:]:
    R=[]
    for k,f in enumerate(frames(v)):
        dist=np.abs(255-f.astype(np.int16)).sum(2).astype(float)
        dist=np.clip(dist,0,300)
        b=dist[:690]; s=dist[690:]
        bprof=b.max(0); sprof=s.max(0); sv=s.max(1)
        bL,bR=sub_edges(bprof,60)
        sL,sR=sub_edges(sprof,60); sT,sB=sub_edges(sv,60)
        sL2,sR2=sub_edges(sprof,25)
        R.append([k,bL,bR,sL,sR,sT+690,sB+690,sL2,sR2])
    R=np.array(R,float)
    out[v]=R.tolist()
    k=R[:,0]; t=k/24
    full=(R[:,1]>1)&(R[:,2]<1918)
    blen=R[full,2]-R[full,1]
    ok=(R[:,3]>1)&(R[:,4]<1918)&(k>=1)
    slen=R[ok,4]-R[ok,3]; slen2=R[ok,8]-R[ok,7]; shgt=R[ok,6]-R[ok,5]
    print('==',v,'n',len(R),'boat len px med %.1f (n=%d, min %.1f max %.1f)'%(np.median(blen),full.sum(),blen.min() if len(blen) else 0, blen.max() if len(blen) else 0))
    print('   shark len px thr60 %.1f thr25 %.1f  height %.1f'%(np.median(slen),np.median(slen2),np.median(shgt)))
    # boat velocity: fit each visible edge, frames>=1
    for j,nm in [(1,'bL'),(2,'bR')]:
        m=(k>=1)&(R[:,j]>1)&(R[:,j]<1918)
        if m.sum()>5:
            p=np.polyfit(t[m],R[m,j],1); p2=np.polyfit(t[m],R[m,j],2)
            print('   boat %s v=%.2f px/s  (quad a=%.2f)'%(nm,p[0],2*p2[0]))
    for j,nm in [(3,'sL'),(4,'sR'),(7,'sL25'),(8,'sR25')]:
        m=(k>=1)&(R[:,j]>1)&(R[:,j]<1918)
        if m.sum()>5:
            p2=np.polyfit(t[m],R[m,j],2); p1=np.polyfit(t[m],R[m,j],1)
            print('   shark %s lin v=%.2f ; quad a=%.2f v0=%.2f v(1s)=%.2f'%(nm,p1[0],2*p2[0],p2[1],p2[1]+2*p2[0]*1))
json.dump(out,open('/home/user/quantiphy-challenge/research/next/audit3/sim2_03/code/side_all_%s.json'%sys.argv[1],'w'))
