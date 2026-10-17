import numpy as np, json
src=open('fit3d.py').read().split("for name,imax in")[0]
for fval in (700.,711.,722.):
    exec(src.replace("f=711.","f=%r"%fval))
    for name,imax,drop in (('white',37,()),('green',36,()),('green',36,(24,)),('white',37,(23,24))):
        obs[name]=[x for x in obs[name] if x[0] not in drop]
        for ua in (True,False):
            s,I,J,uv,P=fit(name,imax,ua)
            V=lambda j: s.x[3:6]+9.8*down*(j-25)/25.
            Pc=lambda j: traj(s.x,np.array([(j-25)/25.]))[0]
            print('f=%d %s drop=%s %s: range c25=%.3f  |v|c37.5=%.2f  chordA(c38-39)=%.2f chordB(c37-38)=%.2f'%(fval,name,drop,'anch' if ua else 'free',np.linalg.norm(s.x[:3]),np.linalg.norm(V(37.5)),np.linalg.norm(Pc(39)-Pc(38))*25,np.linalg.norm(Pc(38)-Pc(37))*25))
