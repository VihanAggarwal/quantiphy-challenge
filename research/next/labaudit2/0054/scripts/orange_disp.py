from common import *
import json
T=json.load(open(OUT+'/orange_tracks_a_b.json'))
def c(v,k,key='e'):
    o=T[v][k]
    return (o['ecx'],o['ecy']) if key=='e' else (o['mx'],o['my']) if key=='m' else (o['bx'],o['by'])
for v,r05,r10 in [('a',2.3557,1.81),('b',2.24,1.81),('b',2.24,2.70)]:
    for key in 'emb':
        p11=np.array(c(v,11,key)); p12=np.array(c(v,12,key)); p24=np.array(c(v,24,key))
        p_c12=(p11+p12)/2  # capture 12 (dropped) ~ midpoint
        P10=bp(*p24,r10)
        for name,p in [('cap12',p_c12),('cap13',p12)]:
            P05=bp(*p,r05)
            print(v,r05,r10,key,name,'disp=%.4f'%np.linalg.norm(P10-P05))
# label-style prior check: v(0.5) forward difference 
