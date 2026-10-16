# Read-only use of research/labnoise emulator: label-noise factor for qid 2537 if the white-ball track had its true
# (route B, table-plane) depth motion instead of the stored constant-range track.
import sys, pickle, copy, numpy as np
sys.path.insert(0,'/home/user/quantiphy-challenge/research/labnoise')
import emulate as EM
from common import tracks
d=tracks('test')
res=pickle.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0032/capclock.pkl','rb'))
for q,A0 in [(2537,25.0),(2541,31.0)]:
    x=d[q]
    m0=EM.row_model(x,A0,'cm/s',cap=1.6); print(q,'stored track, A=%.0f ->'%A0,{k:m0[k] for k in ('factor','sin_psi','exp_ratio','med_ratio')})
    for r in ['o','x']:
        R=res[(r,'ping','B')]
        fr=R['fr']; P=np.array(R['P'])
        x2=copy.deepcopy(x)
        c=x2['cap']['target']
        c['t']=np.array(fr)/24.; c['P']=P; c['rng']=np.linalg.norm(P,axis=1); c['uv']=np.zeros((len(fr),2))
        for A in [60.,64.,70.]:
            m=EM.row_model(x2,A,'cm/s',cap=None)
            print('  ',r,'routeB track A=%.0f'%A,{k:round(float(m[k]),3) for k in ('factor','sin_psi','exp_ratio','med_ratio')})
