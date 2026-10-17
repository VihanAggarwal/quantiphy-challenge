import numpy as np

def fit_lines(P,minlen=40):
    L=[]
    for j in range(P.shape[1]):
        ok=np.isfinite(P[:,j,0]); 
        if ok.sum()<minlen: continue
        xy=P[ok,j]
        c=xy.mean(0); u,s,vt=np.linalg.svd(xy-c); d=vt[0]
        rms=s[1]/np.sqrt(len(xy))
        L.append((c,d,rms,ok.sum(),j))
    return L
def foe(L):
    # minimize distance of point to lines
    A=[];b=[]
    for c,d,rms,n,j in L:
        nrm=np.array([-d[1],d[0]]); A.append(nrm); b.append(nrm@c)
    A=np.array(A); b=np.array(b)
    x=np.linalg.lstsq(A,b,rcond=None)[0]
    r=A@x-b
    return x,r
for c in ['0303','0305','0307']:
    P=np.load(f'tracks_{c}.npy')
    L=fit_lines(P)
    rms=np.array([l[2] for l in L])
    x,r=foe(L)
    # robust: drop worst
    keep=[l for l,rr in zip(L,r) if abs(rr)<3*np.median(abs(r))+1]
    x2,r2=foe(keep)
    print(c,len(L),'line rms med',np.median(rms),'FOE',x, '->',x2, 'resid med',np.median(abs(r2)))
