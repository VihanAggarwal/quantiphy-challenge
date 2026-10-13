"""Scene links from shared object vocabulary (test question/prior text only).
Two simulation clips (bases) are linked when the object names their questions and priors mention overlap in
distinctive names: weight = sum over shared names of idf = log(N_clips / clips naming it); a name 'X' matches
'adj X' (word-suffix containment). Link if weight >= WMIN and >= KMIN shared names."""
import sys, re, json, math, itertools
from collections import Counter
import numpy as np, pandas as pd
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/big/scenegraph/work'
WMIN, KMIN = 8.0, 2
def norm(x): return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',str(x).lower())).strip()
def vocab(t):
    s=t[t.video_id.str.startswith('simulation')]
    voc={}
    for b,g in s.groupby('base'):
        out=set()
        for col in ('tobj','pobj'):
            for o in g[col].dropna():
                for x in str(o).split('|'):
                    x=norm(x)
                    if x: out.add(x)
        voc[b]=out
    return voc
def nmatch(a,b):
    if a==b: return True
    wa,wb=a.split(),b.split()
    if len(wa)<len(wb): wa,wb=wb,wa
    return wa[-len(wb):]==wb   # shorter is a word-suffix of the longer ('pier' ~ 'wooden pier')
def links(t, wmin=WMIN, kmin=KMIN):
    voc=vocab(t); N=len(voc)
    df=Counter(n for v in voc.values() for n in v)
    idf={n:math.log(N/df[n]) for n in df}
    out=[]
    for a,b in itertools.combinations(sorted(voc),2):
        shared=[]
        for x in voc[a]:
            m=[y for y in voc[b] if nmatch(x,y)]
            if m: shared.append((x,min(m,key=lambda y:abs(len(y)-len(x)))))
        if not shared: continue
        w=sum(max(idf[x],idf[y]) if x==y else min(idf[x],idf[y]) for x,y in shared)
        k=len({x for x,_ in shared})
        if w>=wmin and k>=kmin: out.append((a,b,round(w,2),k,sorted({x for x,_ in shared})))
    return out
if __name__=='__main__':
    t=pd.read_pickle(W+'/TS.pkl')
    fam=t.drop_duplicates('base').set_index('base').fam.to_dict()
    L=links(t)
    new=[l for l in L if fam[l[0]]!=fam[l[1]]]
    print(len(L),'links,',len(new),'across existing families')
    for l in new: print(l[0],l[1],fam[l[0]],fam[l[1]],l[2],l[3],'; '.join(l[4]))
