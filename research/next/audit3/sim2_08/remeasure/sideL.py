from util import *
np.set_printoptions(linewidth=250)
for v in ['0258','0259']:
  F=frames(v); g=F[-1].astype(float).mean(2)
  print(v)
  for y in range(858,900,2):
    print(y, np.round(g[y,510:545]).astype(int))
