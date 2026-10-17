import numpy as np, pandas as pd, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1')
from linfit import fit_track
d=pd.read_csv('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1/e28.csv')
e=d[(d.cy<300)&(d.area>100)].sort_values(['frame','area'],ascending=[True,False]).groupby('frame').first().reset_index()
e=e[(e.frame<=39)|(e.frame>=43)]
t=e.frame.values/24.0; x=e.cx.values; y=e.cy.values
for nh in [1,2,3]:
    r=fit_track(t,x,y,np.linspace(0.9,1.2,61),np.linspace(-0.05,0.05,101),nh)
    print('nh',nh,'P frames',r['P']*24,'dd',r['dd'],'rms',r['rms'])
    for tt in [1.0,2.0]: print('  ',tt,np.round(r['f'](tt),2))
