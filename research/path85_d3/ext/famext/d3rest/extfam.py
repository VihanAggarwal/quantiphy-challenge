"""Extended scene families: scene-graph families (big/scenegraph TS.pkl 'fam') + links the scene graph missed.
New links (test inputs only):
  (V) shared object vocabulary between simulation clips (vocablinks.links: idf weight >= 8, >= 2 shared names),
      each candidate pair whose family contains a D3 clip checked by eye on contact sheets (sheets/*.jpg);
      false matches (generic colour-car / streetlight / door-pillar names across different scenes) are dropped.
  (F) near-identical frames between segmented clips (the scene graph's frame clusters skipped *_segmented clips):
      thumbnail NCC >= 0.95 and gradient NCC >= 0.9 (simulation_0038_segmented ~ simulation_0043_segmented, .966/.908).
  (E) eye-verified links: identical prior text between two simulation clips of different families, kept only when the
      contact sheet shows the same scene (frames/eagle0030.jpg: simulation_0030 shows the beach rock, sea and eagle of
      the 0022-0044 series; its prior 'speed of the eagle = 12m/s' is 0029's; best frame NCC 0.755 with 0037).
      Rejected identical-prior pairs: 'height of the person = 1.87m' (atrium 0015/0019 vs street 0021) and
      'speed of the person = 1.3m/s' (atrium 0016/0017 vs beach 0025/0031/0037/0038): different scenes.
"""
import sys, re, pickle, itertools
import numpy as np, pandas as pd
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/big/scenegraph/work'
EXT=SP+'/ext/d3rest'
sys.path.insert(0,EXT)
import vocablinks as VL

# eye-verified on contact sheets (EXT/sheets): different scenes despite shared names
EYE_REJECT_PATTERNS=[
    (r'simulation_00(4[5-9]|50)$', r'simulation_011[67]$', 'photo-lab street vs blue fire-escape wall / dark door: different scenes'),
    (r'simulation_0048$', r'simulation_00(5[89]|6\d|74)$', 'photo-lab street vs white-car intersection: different bicycles'),
    (r'simulation_005[26]$', r'simulation_00(5[89]|6\d)$', 'orange-car street vs white-car intersection (streetlights)'),
    (r'simulation_0075$', r'.*', 'colour-car names (turning yellow car) across different car scenes'),
    (r'simulation_0127$', r'.*', 'colour-car names (red/blue/dark green car) across different scenes (0300 red car in sky, 0130 airport)'),
    (r'simulation_0032$', r'.*', 'segmented-only basketball clip: car/person names shared with orange-car street, view not verifiable'),
    (r'simulation_0120$', r'.*', 'not verified (sofa/tv)'),
    (r'simulation_00(5[89]|6\d|74)$', r'simulation_0(08[5-9]|09\d|112|130|149|15[0-3]|299|30\d|31[01])$',
     'colour-car names: white-car intersection vs top-view limo (0085), airport (0092), river bridge (0112), garage (0149), red car in sky (0300)'),
    (r'simulation_0144$', r'.*', 'desert rocket launcher vs festival street (road; tire)'),
]
EYE_ACCEPT=[('simulation_0029','simulation_0030','eye: identical prior "speed of the eagle = 12m/s", same beach rock/sea/eagle (frames/eagle0030.jpg)')]
def rejected(a,b):
    for pa,pb,why in EYE_REJECT_PATTERNS:
        if (re.match(pa,a) and re.match(pb,b)) or (re.match(pa,b) and re.match(pb,a)): return why
    return None
class UF:
    def __init__(s): s.p={}
    def f(s,x):
        s.p.setdefault(x,x)
        while s.p[x]!=x: s.p[x]=s.p[s.p[x]]; x=s.p[x]
        return x
    def u(s,a,b): s.p[s.f(a)]=s.f(b)
def frame_links(ncc_min=0.95, gncc_min=0.9):
    S=pd.read_pickle(W+'/sim.pkl')
    base=lambda v: re.sub(r'(_segmented|[sxX])$','',v)
    X=S[(S.ncc>=ncc_min)&(S.gncc>=gncc_min)&(S.ar_a==S.ar_b)&~S.a.str.startswith('captured')&~S.b.str.startswith('captured')]
    return [(base(a),base(b),'frame ncc=%.3f gncc=%.3f'%(n,g)) for a,b,n,g in zip(X.a,X.b,X.ncc,X.gncc) if base(a)!=base(b)]
def build(t=None, verbose=False):
    if t is None: t=pd.read_pickle(W+'/TS.pkl')
    fam=t.drop_duplicates('base').set_index('base').fam.to_dict()
    d3fams={f for f,c in zip(t.fam,t.category) if c=='D3'}
    cand=[(a,b,'vocab w=%.1f k=%d: %s'%(w,k,'; '.join(n))) for a,b,w,k,n in VL.links(t)]+frame_links()+list(EYE_ACCEPT)
    acc,rej=[],[]
    for a,b,why in cand:
        if a not in fam or b not in fam or fam[a]==fam[b]: continue
        if not (fam[a] in d3fams or fam[b] in d3fams): continue
        r=rejected(a,b)
        (rej if r else acc).append((a,b,why if not r else r))
    uf=UF()
    for b in fam: uf.u(b,fam[b])
    for a,b,_ in acc: uf.u(a,b)
    # canonical name: smallest original family id in the component
    comp={}
    for b in fam: comp.setdefault(uf.f(b),set()).add(fam[b])
    canon={r:min(s) for r,s in comp.items()}
    fam_ext={b:canon[uf.f(b)] for b in fam}
    t=t.copy(); t['fam_old']=t.fam; t['fam']=t.base.map(fam_ext)
    if verbose:
        print('accepted',len(acc)); [print('  +',x) for x in acc]
        print('rejected',len(rej)); [print('  -',x) for x in rej]
    return t, acc, rej
if __name__=='__main__':
    t,acc,rej=build(verbose=True)
    ch=t[t.fam!=t.fam_old].drop_duplicates('base')
    print(ch[['base','fam_old','fam']].to_string())
    t.to_pickle(EXT+'/work/TS_ext.pkl')
