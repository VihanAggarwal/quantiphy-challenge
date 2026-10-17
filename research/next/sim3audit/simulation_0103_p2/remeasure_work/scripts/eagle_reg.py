import numpy as np, sys
from reg import *
E={'C1':dict(p1=(457.5,244.7),p2=(865.0,255.0),D=(100.1405,99.5206)),
   'C2':dict(p1=(345.7,617.7),p2=(590.5,684.7),D=(175.3081,172.9881))}
def eag(n,**over):
    F=frame_of(n,**over); e=E[n]
    Q1=to_boat(F,F['cam'].pt(*e['p1'],e['D'][0])); Q2=to_boat(F,F['cam'].pt(*e['p2'],e['D'][1]))
    return Q1,Q2
if __name__=='__main__':
  for n in ['C1','C2']:
    Q1,Q2=eag(n); print(n,'eagle t1',np.round(Q1,2),'t2',np.round(Q2,2),'|d|',round(np.linalg.norm(Q2-Q1),2), 'dir',np.round((Q2-Q1)/np.linalg.norm(Q2-Q1),3))
