from util import *
np.set_printoptions(linewidth=250)
for v in ['0257','0258','0259','0260']:
    F=frames(v)
    f=np.mean([F[i].astype(float) for i in (0,39)],0) if False else F[-1].astype(float)
    g=f.mean(2)
    print('clip',v)
    # vertical profile at x=1300 (no objects), rows 855-920
    col=g[855:920,1290:1310].mean(1)
    print(' vprof x1300 y855..919:',np.round(col).astype(int))
    # horizontal profile along wood strip rows 899-908 near ends
    row=g[899:908,:].mean(0)
    print(' wood row L 505..535:',np.round(row[505:535]).astype(int))
    print(' wood row R 1525..1555:',np.round(row[1525:1555]).astype(int))
