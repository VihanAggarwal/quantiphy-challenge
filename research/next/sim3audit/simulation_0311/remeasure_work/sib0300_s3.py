import numpy as np, json
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work/'
T=json.load(open(W+'sib0300/tracks.json'))
tr={int(i):{int(k):np.array(v) for k,v in t.items()} for i,t in T.items()}
tr={i:t for i,t in tr.items() if len(t)>=12}
# line fits
lines=[];keep=[]
for i,t in tr.items():
    P=np.array(list(t.values()))
    mu=P.mean(0); U,S,Vt=np.linalg.svd(P-mu)
    d=Vt[0]; n=Vt[1]
    res=(P-mu)@n
    span=np.ptp((P-mu)@d)
    if span<40: continue
    lines.append((n,n@mu,np.sqrt((res**2).mean()),span)); keep.append(i)
print('lines',len(lines),'median rms perp',np.median([l[2] for l in lines]))
def vp_fit(lines,w=None):
    A=np.array([l[0] for l in lines]); b=np.array([l[1] for l in lines])
    if w is None: w=np.array([l[3] for l in lines])
    v=np.linalg.lstsq(A*w[:,None],b*w,rcond=None)[0]
    return v,A@v-b
v,r=vp_fit(lines)
for it in range(3):
    good=np.abs(r)<3*np.median(np.abs(r))+0.5
    v,_=vp_fit([l for l,g in zip(lines,good) if g]); r=np.array([l[0]@v-l[1] for l in lines])
print('VP',v,'inliers',good.sum(),'median |r|',np.median(np.abs(r)))
# bootstrap VP
rng=np.random.default_rng(0); L=[l for l,g in zip(lines,good) if g]
bs=[vp_fit([L[j] for j in rng.integers(0,len(L),len(L))])[0] for _ in range(200)]
print('VP sd',np.std(bs,0))
np.save(W+'sib0300/vp.npy',v)
# 1/d matrix
ids=[i for i,g in zip(keep,good) if g]
frames=list(range(2,72))
M=np.full((len(ids),72),np.nan)
for a,i in enumerate(ids):
    for k,p in tr[i].items(): M[a,k]=1.0/np.linalg.norm(p-v)
# ALS: M[a,k] = al[a] + be[a]*s[k]
s=np.array([np.nan]*72)
# init s from frame index
s=np.arange(72,dtype=float)
obs=~np.isnan(M)
for it in range(200):
    al=np.zeros(len(ids)); be=np.zeros(len(ids))
    for a in range(len(ids)):
        o=obs[a]; X=np.c_[np.ones(o.sum()),s[o]]; al[a],be[a]=np.linalg.lstsq(X,M[a,o],rcond=None)[0]
    for k in range(72):
        o=obs[:,k]
        if o.sum()<3: s[k]=np.nan; continue
        s[k]=np.sum(be[o]*(M[o,k]-al[o]))/np.sum(be[o]**2)
    # gauge: s(24)=0, s(48)=1
    s0,s1=s[24],s[48]; s=(s-s0)/(s1-s0)
res=[]
for a in range(len(ids)):
    o=obs[a]&~np.isnan(s); res.append(((M[a,o]-al[a]-be[a]*s[o])/be[a]))
print('resid (in s units) rms',np.sqrt(np.nanmean(np.concatenate(res)**2)))
cnt=obs.sum(0)
for k in range(72): print(k,cnt[k],None if np.isnan(s[k]) else round(s[k],5), '' if k<3 or np.isnan(s[k]) or np.isnan(s[k-1]) else round(s[k]-s[k-1],5))
np.save(W+'sib0300/s_profile.npy',s)
