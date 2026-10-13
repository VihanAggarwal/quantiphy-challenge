from pseudo2 import *
rng=np.random.default_rng(0)
# observed pairwise |diff| in groups >=2 bases (size and speed separately)
def obs_diffs(kind):
    d=[]
    for gr in G:
        if gr['kind']!=kind: continue
        v=list(gr['bl'].values())
        for i in range(len(v)):
            for j in range(i+1,len(v)): d.append(abs(v[i]-v[j]))
    return np.array(d)
qs=[0.5,0.75,0.9,0.97]
def sim_err(n,df,s):
    return s*rng.standard_t(df,size=n)
for kind in ('size','speed'):
    od=obs_diffs(kind); oq=np.quantile(od,qs)
    best=None
    for df in (1.5,2,3,5,10,50):
        for s in np.linspace(0.005,0.15,59):
            e=sim_err(20000,df,s); f=sim_err(20000,df,s); sq=np.quantile(np.abs(e-f),qs)
            err=np.sum((np.log(sq)-np.log(oq))**2)
            if best is None or err<best[0]: best=(err,df,s,sq)
    print(kind,'observed |diff| quantiles',oq.round(3),'fit df',best[1],'scale',round(best[2],4),'sim q',best[3].round(3))
    df,s=best[1],best[2]
    # real vs pseudo gain on synthetic groups with the real group sizes, cap and stat as configured
    for cap,stat in ((10,'median'),(10,'mean'),(0.4,'mean'),(0.4,'trim'),(0.4,'median')):
        real=[];pseudo=[];rawabs=[]
        for rep in range(40):
            for gr in G:
                if gr['kind']!=kind or len(gr['bl'])<2: continue
                n=len(gr['bl']); e=sim_err(n,df,s)
                if e.max()-e.min()>cap: continue
                # real: full pool over all bases (deployed rule pools all n)
                if n>=2:
                    pv=agg(e,stat) if n>=3 else np.mean(e)
                    real.append((S(np.full(n,pv))-S(e)).mean()); rawabs.append(S(e).mean())
                if n>=3:
                    for j in range(n):
                        oth=np.delete(e,j)
                        if len(oth)<2: continue
                        pv=agg(oth,stat)
                        pseudo.append((S(np.full(len(oth),pv)-e[j])-S(oth-e[j])).mean())
        print(f'   cap {cap} {stat:6}: synthetic real gain/row {np.mean(real):+.4f} (raw score {np.mean(rawabs):.3f}); synthetic pseudo gain {np.mean(pseudo):+.4f}')
