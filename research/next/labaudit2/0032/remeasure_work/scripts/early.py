import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/scripts')
from geom import *
base='/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/'
def capidx(j): return np.where(j>=36, j+2, j+1)
Ca=np.load(base+'circ_a.npy'); Cx=np.load(base+'circ_ax.npy')
Ba=np.load(base+'white_rows_0032.npy'); Bx=np.load(base+'white_rows_0032x.npy')
hc=137.3*(n@ray(721.3,431.95))
print('hc',hc)
for name,C in (('circ_a',Ca),('circ_ax',Cx),('blob_a',Ba[:,:3]),('blob_x',Bx[:,:3])):
    j=C[:,0]; c=capidx(j)
    P=np.array([on_plane(u,v,hc) for u,v in C[:,1:3]])
    s=[]
    for k in range(len(j)-1):
        if j[k]<33: continue
        dc=c[k+1]-c[k]; s.append('c%d->%d:%.0f'%(c[k],c[k+1],np.linalg.norm(P[k+1]-P[k])*25/dc))
    print(name,' '.join(s[:8]))
