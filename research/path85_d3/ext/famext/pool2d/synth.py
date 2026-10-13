import sys
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/pool2d/rebuild')
from rule import *
TAU,CAP2,SMAX=0.15,0.25,0.35
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
Trows=set(int(l.split()[0]) for l in open(SP+'/big/scene_graph/T_list.txt') if not l.startswith('====='))
G=build_groups(t,unit='cam',cats=('S2','D2'))
G=[g for g in G if len(g['ul'])>=2 and not any(q in Trows for m in g['members'].values() for q,_ in m)]
def rule_pv(votes):
    votes=list(votes)
    if len(votes)<2: return None
    if len(votes)<=3 and max(votes)-min(votes)>SMAX: return None
    return pooled_value(votes,TAU,CAP2,'trimmed')
# observed pairwise differences of camera means
od=np.array([abs(a-b) for g in G for i,a in enumerate(g['ul'].values()) for b in list(g['ul'].values())[i+1:]])
qs=[0.25,0.5,0.75,0.9,0.97]; oq=np.quantile(od,qs)
rng=np.random.default_rng(0)
best=None
for df in (1.5,2,2.5,3,4,6,10,30):
    for s in np.linspace(0.005,0.12,47):
        e=s*rng.standard_t(df,40000); f=s*rng.standard_t(df,40000); sq=np.quantile(np.abs(e-f),qs)
        err=np.sum((np.log(sq)-np.log(oq))**2)
        if best is None or err<best[0]: best=(err,df,s,sq)
_,df,s,sq=best
print('observed |diff| q',oq.round(4),'fit df',df,'s',round(s,4),'sim q',sq.round(4))
shape=[(len(g['ul']),[len(m) for m in g['members'].values()]) for g in G]
def run(bias_sd=0.0, reps=300):
    real=[];pse=[];realall=[]
    for r in range(reps):
        for n,rows in shape:
            b=rng.normal(0,bias_sd)                 # shared family bias
            c=b+s*rng.standard_t(df,n)              # camera errors
            pv=rule_pv(c)
            if pv is not None:
                for u in range(n): real.append((S([pv])[0]-S([c[u]])[0], rows[u]))
            if n>=3:
                for j in range(n):
                    oth=np.delete(c,j); p2=rule_pv(oth)
                    if p2 is None: continue
                    for u in range(n-1): pse.append((S([p2-c[j]])[0]-S([oth[u]-c[j]])[0], 1))
    R=np.array(real); P=np.array(pse)
    return np.average(R[:,0],weights=R[:,1]), np.average(P[:,0],weights=P[:,1])
for bsd in (0.0,0.03,0.06,0.1):
    a,b=run(bsd)
    print('shared family bias sd %.2f: synthetic REAL gain per changed row %+.4f ; synthetic PSEUDO gain %+.4f'%(bsd,a,b))
