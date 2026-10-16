import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0020/scripts')
from geo import bp
import numpy as np
far=[(705,115),(705,60),(710,150),(700,30),(715,200)]
near=[(165,450),(150,400),(120,300),(200,500),(100,350),(250,560)]
for f in (690,711,730):
  vals=[]
  for a in far:
    for b in near:
      vals.append(np.linalg.norm(bp(*a,3.237,f)-bp(*b,1.58,f))*100)
  print(f, 'min %.1f max %.1f med %.1f'%(min(vals),max(vals),np.median(vals)), 'centroids %.1f'%(np.linalg.norm(bp(705,115,3.237,f)-bp(165,450,1.58,f))*100))
