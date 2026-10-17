import numpy as np
from frame3d import axes
from sweep import to3d
pairs={'fin_top':(((1378,821),0.008866),((1950,712),0.008146)),
       'pod_front':(((1414,798),0.00823),((1692,746),0.00789)),
       'pod_rear':(((1622,982),0.00895),((1911,918),0.00856))}
for f in [3400,3500,3550,3600,3650,3700,3800,4000]:
    V,S,U=axes(f)
    out=[]
    for k,((pa,qa),(pb,qb)) in pairs.items():
        A=to3d(pa,qa,f,18.49/24)[0]; B=to3d(pb,qb,f,18.49/24)[0]
        d=B-A
        ang=np.degrees(np.arcsin(d@V/np.linalg.norm(d)))
        out.append('%s: |d|=%.2f angle-from-perp-to-V=%+.2fdeg dUp=%+.2f'%(k,np.linalg.norm(d),ang,d@U))
    print(f,' | '.join(out))
