import numpy as np
from common import *
exec(open('wbplane.py').read().split('frames=[n')[0])
sets={'manual':[(771,313),(818,296),(895,344),(842,371)],
      'manual_b':[(770,314),(822,295),(896,345),(842,372)],
      'quadfit':[(765.4,309.5),(835.1,292.0),(895.4,347.0),(843.3,370.1)]}
for f,(p,r) in {700:(39.34,8.43),711:(38.93,8.53),722:(38.50,8.66)}.items():
    nm=normal(p,r)
    for k,c in sets.items():
        s,cs,P=geom(np.array(c,float),nm,1.0,f)
        print(f,k,'sides/h L-T %.4f T-R %.4f R-B %.4f B-L %.4f'%tuple(s),'cos',np.round(cs,3),
              ' height(sides)=%.4f width(open/bottom)=%.4f'%((s[0]+s[2])/2,(s[1]+s[3])/2))
