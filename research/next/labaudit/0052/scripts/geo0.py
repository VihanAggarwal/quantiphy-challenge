import numpy as np
F=711.0; CX=640; CY=360
def P(u,v,r,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return r*d/np.linalg.norm(d)
def D(a,b): return float(np.linalg.norm(a-b))
R={'yoga':2.612,'shoe':2.231,'bin':2.977,'bb':1.9365}
C={'shoe':(285,654),'bb':(803,668),'bin':(728,538),'yoga1':(570,543)}
for f in (690,711,730):
    Ps={k:P(*C[k],R['yoga' if k=='yoga1' else k],f) for k in C}
    print(f,'bb-shoe %.3f bin-shoe %.3f bin-bb %.3f yoga1-shoe %.3f'%(D(Ps['bb'],Ps['shoe']),D(Ps['bin'],Ps['shoe']),D(Ps['bin'],Ps['bb']),D(Ps['yoga1'],Ps['shoe'])))
