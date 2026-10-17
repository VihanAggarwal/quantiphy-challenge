from common import *
import json
from fit_a import gd
T=json.load(open(OUT+'/orange_tracks_a_b.json'))
db=np.load(OUT+'/b_down.npy')
for v,g in [('a',gd(0)),('b',db)]:
    print('camera',v)
    prev=None
    for k in range(0,30):
        o=T[v][k]
        if o is None: continue
        s=o['eb']  # minor axis
        c=(o['ecx'],o['ecy'])
        r=F*0.232/s; P=r*ray(*c)
        sp='' if prev is None else ' step=%.3f m (%.2f m/s)'%(np.linalg.norm(P-prev[1]), np.linalg.norm(P-prev[1])/(tcap(k)-tcap(prev[0])))
        print('  k=%d cap=%d c=(%.1f,%.1f) minor=%.1f r_c=%.3f down=%.3f%s'%(k,cap(k),c[0],c[1],s,r,P@g,sp))
        prev=(k,P)
