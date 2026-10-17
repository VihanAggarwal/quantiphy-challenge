import numpy as np, json
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work/'
T=json.load(open(W+'taillights.json'))
vD=np.load(W+'vp.npy')
A=[];b=[]
ks=range(31,72)
for k in ks:
    p=np.array(T['TLL'][str(k)]); q=np.array(T['TLR'][str(k)])
    d=q-p; n=np.array([-d[1],d[0]]); n/=np.linalg.norm(n)
    A.append(n); b.append(n@p)
A=np.array(A); b=np.array(b)
vL=np.linalg.lstsq(A,b,rcond=None)[0]
r=A@vL-b
print('vL',vL,'rms px',np.sqrt((r**2).mean()))
# bootstrap
rng=np.random.default_rng(1); bs=[]
for _ in range(500):
    j=rng.integers(0,len(b),len(b)); bs.append(np.linalg.lstsq(A[j],b[j],rcond=None)[0])
bs=np.array(bs); print('vL boot sd',bs.std(0), 'pct', np.percentile(bs[:,0],[5,50,95]))
# check TL tracks through vD
for nm in ['TLL','TLR']:
    P=np.array([T[nm][str(k)] for k in ks])
    mu=P.mean(0); U,S,Vt=np.linalg.svd(P-mu); n=Vt[1]
    print(nm,'line rms',np.sqrt((((P-mu)@n)**2).mean()),'dist of vD to line',(vD-mu)@n)
c=np.array([1280,720.])
f2=-(vD-c)@(vL-c); print('f from vD,vL',np.sqrt(f2) if f2>0 else f2)
for v in bs[:0]: pass
fs=[np.sqrt(-(vD-c)@(v-c)) for v in bs]; print('f boot pct',np.percentile(fs,[5,50,95]))
np.save(W+'vL.npy',vL)
