from util import *
np.set_printoptions(linewidth=250)
F=frames('0258'); g=F[-1].astype(float).mean(2)
for y in range(860,900,2):
    print(y, np.round(g[y,1515:1545]).astype(int))
