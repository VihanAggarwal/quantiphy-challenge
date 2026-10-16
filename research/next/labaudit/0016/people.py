import numpy as np
f=711.;cx,cy=640,360
def bp(u,v,r):
    d=np.array([u-cx,v-cy,f]);return r*d/np.linalg.norm(d)
near=[(30,150),(60,300),(100,400),(100,450),(150,500),(200,450),(120,600),(60,200)]
far=[(1100,120),(1090,190),(1080,250),(1050,320),(1000,380),(1120,60)]
print('far\\near',near)
for fp in far:
    print(fp,[round(100*np.linalg.norm(bp(*fp,2.372)-bp(*n,0.843)),1) for n in near])
