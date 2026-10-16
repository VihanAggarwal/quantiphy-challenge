import numpy as np
def nvec(a,b): return np.array([np.sin(b)*np.cos(a), np.cos(b)*np.cos(a), np.sin(a)])
pts=[('book',666.4,617.9,2.082,0.018),('cup',564.3,424.0,2.516,0.06),('ball',985.8,369.6,2.925,0.116),
     ('wb62',705.4,415.3,2.815,0.008),('bag62',837.3,329.1,3.307,0.01),('bin10',797.7,379.5,2.73,None)]
f=711.
for pitch,roll,name in [(39.25,-8.5,'whiteboard normal'),(34.46,-10.42,'VP normal'),(40.2,-10.0,'zdepth-fit')]:
    dn=nvec(np.radians(pitch),np.radians(roll))
    for mode in ('range','zdepth'):
        X={}
        for nm,u,v,r,z in pts:
            d=np.array([(u-640)/f,(v-360)/f,1.0])
            p=r*d/np.linalg.norm(d) if mode=='range' else r*d
            if nm=='ball': p=p+0.116*d/np.linalg.norm(d)
            X[nm]=p
        H=X['book']@dn+0.018
        s=' '.join('%s z=%.3f'%(nm,H-X[nm]@dn) for nm,_,_,_,_,_ in [(p[0],0,0,0,0,0) for p in pts])
        print('%-18s %-6s H %.3f | %s'%(name,mode,H,s))
