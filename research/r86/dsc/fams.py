import sys; sys.path.insert(0,'/home/user/quantiphy-challenge'); sys.path.insert(0,'/home/user/quantiphy-challenge/research/r86/dsc')
from common import *
from qp import postprocess as PP
import pickle
d=load()
df=PP._questions(d.assign(category=d.cg), video_root=f'{ROOT}/data/QuantiPhy')
facts=PP._parse_facts(df)
frames=PP.FrameCache(PP.DEFAULT_CACHE)
links=PP.scene_links(df,facts,frames)
fam=PP.scene_families(df,links)
mfam=PP.scene_families(df,links,PP.MOTION_LINKS)
pickle.dump(dict(links=links,fam=fam,mfam=mfam),open(f'{ROOT}/research/r86/dsc/fams.pkl','wb'))
print({k:len(v) for k,v in links.items()})
